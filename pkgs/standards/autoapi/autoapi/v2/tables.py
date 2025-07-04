from .mixins import Base, GUIDPk, Timestamped, TenantBound, Principal, RelationEdge, Timestamped, MaskableEdge


# ───────── tenancy core ──────────────────────────────────────────────────
class User(Base, GUIDPk, Timestamped, TenantBound, Principal):
    __tablename__ = "users"
    email        = Column(String, unique=True)

class Group(Base, GUIDPk, Timestamped, TenantBound, Principal):
    __tablename__ = "groups"
    name         = Column(String)

# ───────── RBAC core ──────────────────────────────────────────────────
class Role(Base, GUIDPk, Timestamped, TenantBound):
    __tablename__ = "roles"
    slug         = Column(String, unique=True)
    global_mask  = Column(Integer, default=0)

class RolePerm(Base, GUIDPk, Timestamped, TenantBound,
               RelationEdge, MaskableEdge):
    __tablename__ = "role_perms"
    role_id       = Column(UUID, ForeignKey("roles.id"))
    target_table  = Column(String)
    target_id     = Column(UUID)                # row or sentinel

class RoleGrant(Base, GUIDPk, Timestamped, TenantBound,
                RelationEdge):
    __tablename__ = "role_grants"
    principal_id  = Column(UUID)                # FK to principal row
    role_id       = Column(UUID, ForeignKey("roles.id"))


# ───────── Audit  ───────────────────────────────────────────────────────
class Change(Base):
    __tablename__ = "changes"
    seq          = Column(BigInteger, primary_key=True, autoincrement=True)
    at           = Column(DateTime, default=dt.datetime.utcnow)
    actor_id     = Column(UUID, ForeignKey("users.id"))
    table_name   = Column(String)
    row_id       = Column(UUID)
    action       = Column(String)       # insert | update | delete
    diff         = Column(JSONB)
