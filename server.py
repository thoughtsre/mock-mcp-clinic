import os
import threading
from typing import Dict, List, Optional
from http.server import BaseHTTPRequestHandler, HTTPServer

from mcp.server.fastmcp import FastMCP


mcp = FastMCP(name="clinic-mcp")


DOCTORS: List[Dict[str, str]] = [
	{"name": "Dr. Alice Smith", "specialty": "Cardiology"},
	{"name": "Dr. Bob Jones", "specialty": "Dermatology"},
	{"name": "Dr. Carol Nguyen", "specialty": "Orthopedics"},
	{"name": "Dr. David Patel", "specialty": "Neurology"},
	{"name": "Dr. Eva Garcia", "specialty": "General Practice"},
]


CLINIC_CONTACT: Dict[str, str] = {
	"name": "Wellness Family Clinic",
	"phone": "+1-555-0100",
	"email": "contact@wellnessfamilyclinic.example",
	"address": "123 Health St, Wellness City, CA 94000",
}


@mcp.tool()
def list_doctors() -> List[Dict[str, str]]:
	"""Return the clinic's available doctors and their specialties."""
	return DOCTORS


@mcp.tool()
def clinic_contact() -> Dict[str, str]:
	"""Return the clinic's contact information."""
	return CLINIC_CONTACT


def _match_specialty_from_condition(condition: str) -> str:
	condition_lower = condition.lower()
	keyword_to_specialty = {
		"heart": "Cardiology",
		"cardio": "Cardiology",
		"skin": "Dermatology",
		"rash": "Dermatology",
		"bone": "Orthopedics",
		"joint": "Orthopedics",
		"knee": "Orthopedics",
		"brain": "Neurology",
		"headache": "Neurology",
		"migraine": "Neurology",
	}
	for keyword, specialty in keyword_to_specialty.items():
		if keyword in condition_lower:
			return specialty
	return "General Practice"


@mcp.tool()
def make_appointment(
	condition: str,
	preferred_time: Optional[str] = None,
	requestor_name: Optional[str] = None,
	requestor_phone: Optional[str] = None,
) -> Dict[str, str]:
	"""Create a mock appointment based on the requestor's condition.

	Args:
		condition: The patient's condition or reason for visit.
		preferred_time: Optional preferred time (e.g., "2025-09-15 10:00").
		requestor_name: Optional name of the person booking.
		requestor_phone: Optional phone number for confirmation.

	Returns:
		A confirmation object for the appointment.
	"""
	matched_specialty = _match_specialty_from_condition(condition)
	assigned_doctor = next(
		(doc for doc in DOCTORS if doc["specialty"] == matched_specialty),
		next(doc for doc in DOCTORS if doc["specialty"] == "General Practice"),
	)

	confirmation: Dict[str, str] = {
		"status": "confirmed",
		"doctor": assigned_doctor["name"],
		"specialty": assigned_doctor["specialty"],
		"condition": condition,
		"preferred_time": preferred_time or "next available",
		"contact_phone": requestor_phone or CLINIC_CONTACT["phone"],
		"clinic": CLINIC_CONTACT["name"],
		"clinic_address": CLINIC_CONTACT["address"],
	}
	if requestor_name:
		confirmation["requestor_name"] = requestor_name

	return confirmation


class _HealthHandler(BaseHTTPRequestHandler):
	def do_GET(self) -> None:
		if self.path in ("/", "/health", "/healthz", "/status"):
			self.send_response(200)
			self.send_header("Content-Type", "text/plain; charset=utf-8")
			self.end_headers()
			self.wfile.write(b"ok")
			return

		self.send_response(404)
		self.end_headers()

	# Silence default logging to stderr
	def log_message(self, fmt: str, *args) -> None:  # type: ignore[override]
		return


def _start_healthcheck_server(host: str, port: int) -> None:
	httpd = HTTPServer((host, port), _HealthHandler)
	thread = threading.Thread(target=httpd.serve_forever, daemon=True)
	thread.start()


if __name__ == "__main__":
	host = os.getenv("HOST", "0.0.0.0")
	port = int(os.getenv("PORT", "8000"))

	# Start an HTTP healthcheck server so ECS can probe container health
	health_host = os.getenv("HEALTH_HOST", "0.0.0.0")
	health_port = int(os.getenv("HEALTH_PORT", "8080"))
	_start_healthcheck_server(health_host, health_port)

	# Start the MCP server over HTTP/SSE so it remains alive on ECS
	mcp.run(transport="sse")


