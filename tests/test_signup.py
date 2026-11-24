import unittest

from fastapi.testclient import TestClient

from src.app import activities, app


class SignupTests(unittest.TestCase):
    def test_student_cannot_sign_up_twice_for_same_activity(self):
        activity_name = "Chess Club"
        email = "test-student@mergington.edu"
        participants = activities[activity_name]["participants"]
        original_participants = participants.copy()
        client = TestClient(app)

        try:
            first_response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email},
            )
            duplicate_response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email},
            )

            self.assertEqual(first_response.status_code, 200)
            self.assertEqual(duplicate_response.status_code, 400)
            self.assertEqual(participants.count(email), 1)
        finally:
            participants[:] = original_participants


if __name__ == "__main__":
    unittest.main()
