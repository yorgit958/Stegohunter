from celery import Celery

# Configure the Gateway Publisher to match the Orchestration Worker
# Broker points to the docker Redis instance
celery_publisher = Celery(
    "gateway_publisher",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1"
)

celery_publisher.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC"
)
