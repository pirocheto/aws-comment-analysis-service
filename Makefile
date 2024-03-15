update:
	sam build
	sam deploy --resolve-image-repos --force-upload

test-local-GetDataFunction:
	sam local invoke GetDataFunction -e events/GetData.json | jq

test-remote-CreateReportStateMachine:
	sam remote invoke CreateReportStateMachine --event-file events/GetData.json | jq

test-remote-GetDataFunction:
	sam remote invoke GetDataFunction --event-file events/GetData.json | jq

test-remote-TransformDataFunction:
	sam remote invoke TransformDataFunction --event-file events/TransformData.json | jq

test-remote-FormatDataFunction:
	sam remote invoke FormatDataFunction --event-file events/FormatData.json | jq

test-remote-AnalyzeDataFunction:
	sam remote invoke AnalyzeDataFunction --event-file events/AnalyzeData.json | jq

test-remote-CreateReport:
	sam remote invoke CreateReportFunction --event-file events/CreateReport.json | jq

build-TransformDataFunction:
	docker build --platform linux/arm64 -t ${aws_ecr_repository.repository.repository_url}:latest .
	aws ecr get-login-password --region ${var.region} | docker login --username AWS --password-stdin ${aws_ecr_repository.repository.repository_url}
	docker push ${aws_ecr_repository.repository.repository_url}:latest
