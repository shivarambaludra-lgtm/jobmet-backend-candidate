from locust import HttpUser, task, between, events
import random

class JobMetUser(HttpUser):
    """Simulated user for load testing"""
    
    wait_time = between(1, 3)
    host = "http://localhost:8000"
    
    def on_start(self):
        """Login before running tests"""
        response = self.client.post("/api/v1/auth/login", data={
            "username": f"user{random.randint(1, 100)}@test.com",
            "password": "testpass123"
        })
        
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.client.post("/api/v1/auth/register", json={
                "email": f"user{random.randint(1, 100)}@test.com",
                "password": "testpass123",
                "full_name": "Test User"
            })
            self.on_start()
    
    @task(5)
    def search_jobs(self):
        """Test search endpoint (highest frequency)"""
        queries = [
            "python developer",
            "java engineer",
            "data scientist remote",
            "frontend react developer",
            "devops engineer"
        ]
        
        self.client.post(
            "/api/v1/search/jobs",
            json={"query": random.choice(queries)},
            headers=self.headers,
            name="/api/v1/search/jobs"
        )
    
    @task(3)
    def get_bookmarks(self):
        """Test bookmarks endpoint"""
        self.client.get(
            "/api/v1/bookmarks",
            headers=self.headers,
            name="/api/v1/bookmarks"
        )
    
    @task(2)
    def get_recommendations(self):
        """Test recommendations endpoint"""
        self.client.get(
            "/api/v1/recommendations?limit=20",
            headers=self.headers,
            name="/api/v1/recommendations"
        )
    
    @task(2)
    def get_applications(self):
        """Test applications endpoint"""
        self.client.get(
            "/api/v1/applications",
            headers=self.headers,
            name="/api/v1/applications"
        )
    
    @task(1)
    def get_analytics(self):
        """Test analytics dashboard"""
        self.client.get(
            "/api/v1/analytics/dashboard?days=30",
            headers=self.headers,
            name="/api/v1/analytics/dashboard"
        )
    
    @task(1)
    def health_check(self):
        """Test health endpoint"""
        self.client.get("/health", name="/health")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("🚀 Load test starting...")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("✅ Load test complete!")
    
    stats = environment.stats
    print(f"\n📊 Summary:")
    print(f"Total requests: {stats.total.num_requests}")
    print(f"Total failures: {stats.total.num_failures}")
    print(f"Average response time: {stats.total.avg_response_time:.2f}ms")
    print(f"Requests per second: {stats.total.current_rps:.2f}")

# Run with: locust -f tests/load_test.py --host=http://localhost:8000
