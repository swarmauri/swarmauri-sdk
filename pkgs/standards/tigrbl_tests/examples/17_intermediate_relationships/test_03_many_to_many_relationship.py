"""Example: many-to-many relationships exposed through Tigrbl REST endpoints."""

from __future__ import annotations

import inspect

import httpx
import pytest

from examples._support import pick_unique_port, start_uvicorn, stop_uvicorn
from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.types import Column, ForeignKey, Integer, String, relationship


@pytest.mark.asyncio
async def test_many_to_many_relationship_via_rest() -> None:
    """Show a many-to-many relationship with an enrollment model."""

    # Step 1: Define the first "side" of the relationship.
    class Student(Base):
        __tablename__ = "lesson_rel_student"
        __allow_unmapped__ = True

        # Students can enroll in multiple courses.
        id = Column(Integer, primary_key=True)
        name = Column(String, nullable=False)
        enrollments = relationship(
            "Enrollment", back_populates="student", cascade="all, delete-orphan"
        )
        courses = relationship(
            "Course",
            secondary="lesson_rel_enrollment",
            back_populates="students",
            overlaps="enrollments",
        )

    # Step 2: Define the other "side" of the many-to-many relationship.
    class Course(Base):
        __tablename__ = "lesson_rel_course"
        __allow_unmapped__ = True

        # Courses can have multiple students.
        id = Column(Integer, primary_key=True)
        title = Column(String, nullable=False)
        enrollments = relationship(
            "Enrollment", back_populates="course", cascade="all, delete-orphan"
        )
        students = relationship(
            "Student",
            secondary="lesson_rel_enrollment",
            back_populates="courses",
            overlaps="enrollments",
        )

    # Step 3: Define the join model that captures each enrollment.
    class Enrollment(Base):
        __tablename__ = "lesson_rel_enrollment"
        __allow_unmapped__ = True

        # Each enrollment links a student and a course.
        id = Column(Integer, primary_key=True)
        student_id = Column(
            Integer, ForeignKey("lesson_rel_student.id"), nullable=False
        )
        course_id = Column(Integer, ForeignKey("lesson_rel_course.id"), nullable=False)
        student = relationship(
            "Student", back_populates="enrollments", overlaps="courses,students"
        )
        course = relationship(
            "Course", back_populates="enrollments", overlaps="courses,students"
        )

    # Step 4: Build the API with all three models registered.
    api = TigrblApp(engine=mem(async_=False))
    api.include_models([Student, Course, Enrollment])
    init_result = api.initialize()
    if inspect.isawaitable(init_result):
        await init_result

    # Step 5: Mount the API routes on the app.
    app = TigrblApp()
    app.include_router(api.router)
    api.attach_diagnostics(prefix="", app=app)

    # Step 6: Launch uvicorn and exercise the REST endpoints.
    port = pick_unique_port()
    base_url, server, task = await start_uvicorn(app, port=port)
    try:
        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
            # Create a student record.
            create_student = await client.post("/student", json={"name": "Lee"})
            assert create_student.status_code == 201
            student_id = create_student.json()["id"]

            # Create two courses to enroll in.
            create_course_one = await client.post(
                "/course",
                json={"title": "Distributed Systems"},
            )
            create_course_two = await client.post(
                "/course",
                json={"title": "Machine Learning"},
            )
            assert create_course_one.status_code == 201
            assert create_course_two.status_code == 201
            course_one_id = create_course_one.json()["id"]
            course_two_id = create_course_two.json()["id"]

            # Link the student to both courses via enrollments.
            await client.post(
                "/enrollment",
                json={"student_id": student_id, "course_id": course_one_id},
            )
            await client.post(
                "/enrollment",
                json={"student_id": student_id, "course_id": course_two_id},
            )

            # Verify both enrollments exist for the student.
            enrollments = await client.get("/enrollment")
            assert enrollments.status_code == 200
            student_enrollments = [
                item for item in enrollments.json() if item["student_id"] == student_id
            ]
            assert len(student_enrollments) == 2
    finally:
        # Tear down uvicorn cleanly.
        await stop_uvicorn(server, task)
