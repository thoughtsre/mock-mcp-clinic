import importlib


def test_list_doctors_returns_non_empty_list():
	server = importlib.import_module("server")
	result = server.list_doctors()
	assert isinstance(result, list)
	assert len(result) > 0
	for item in result:
		assert "name" in item and "specialty" in item


def test_clinic_contact_contains_required_fields():
	server = importlib.import_module("server")
	contact = server.clinic_contact()
	for key in ("name", "phone", "email", "address"):
		assert key in contact


def test_make_appointment_matches_specialty_keywords():
	server = importlib.import_module("server")
	confirmation = server.make_appointment("I have a skin rash", preferred_time="2025-12-01 09:00")
	assert confirmation["status"] == "confirmed"
	assert confirmation["specialty"] == "Dermatology"
	assert confirmation["preferred_time"] == "2025-12-01 09:00"


def test_make_appointment_defaults_next_available():
	server = importlib.import_module("server")
	confirmation = server.make_appointment("annual checkup")
	assert confirmation["preferred_time"] == "next available"


