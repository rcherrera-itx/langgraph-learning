from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

employee_namespace = ("profiles", "EMP-001")

store.put(
    employee_namespace,
    "profile",
    {"laptop_model": "X1 Carbon"}
)

saved = store.get(employee_namespace, "profile")
other_employee = store.get(
    ("profiles", "EMP-002"),
    "profile"
)

print("Perfil de EMP-001:", saved.value)
print("Perfil de EMP-002:", other_employee)