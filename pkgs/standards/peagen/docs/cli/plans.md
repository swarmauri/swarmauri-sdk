# `peagen plan`

The `plan` command manages persistent plans stored in the Peagen database. Plans
represent structured instructions for different phases of a workflow and can be
locked to prevent further modification.

## Usage

```console
peagen local plan [COMMAND] [ARGS]
```

### create
Create a new plan from a JSON file.

```console
peagen local plan create <doe|evaluation|evolve|analysis> PLAN.json
```

The command prints the generated plan ID.

### read
Fetch an existing plan and print it as JSON.

```console
peagen local plan read <type> PLAN_ID
```

### update
Update a mutable plan using a JSON file. Locked plans cannot be modified.

```console
peagen local plan update <type> PLAN_ID UPDATED.json
```

### lock
Mark a plan as immutable.

```console
peagen local plan lock <type> PLAN_ID
```

### Demonstration

Below is a short example showing how the command can be used. Assume `plan.json` contains a DOE plan definition:

```json
{
  "name": "demo DOE plan",
  "description": "example for docs",
  "data": {"factor": 42}
}
```

Create the plan and capture the generated ID:

```console
$ peagen local -q plan create doe plan.json
123e4567-e89b-12d3-a456-426614174000
```

Read the plan back:

```console
$ peagen local -q plan read doe 123e4567-e89b-12d3-a456-426614174000
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "demo DOE plan",
  "description": "example for docs",
  "data": {"factor": 42},
  "locked": false
}
```

Lock the plan:

```console
$ peagen local -q plan lock doe 123e4567-e89b-12d3-a456-426614174000
```

