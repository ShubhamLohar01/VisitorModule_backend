# Makefile for Lambda ZIP Deployment
# Simplifies common deployment tasks

.PHONY: help build-layer deploy-layer build-package deploy-package deploy-all clean

help:
	@echo "Lambda ZIP Deployment Commands:"
	@echo "  make build-layer      - Build Lambda layer with dependencies"
	@echo "  make deploy-layer      - Deploy layer to AWS Lambda"
	@echo "  make build-package     - Build deployment package (code only)"
	@echo "  make deploy-package   - Deploy function to AWS Lambda"
	@echo "  make deploy-all       - Build and deploy everything"
	@echo "  make clean            - Clean build artifacts"

build-layer:
	@chmod +x build-layer.sh
	@./build-layer.sh

deploy-layer:
	@chmod +x deploy-layer.sh
	@./deploy-layer.sh

build-package:
	@chmod +x build-package.sh
	@./build-package.sh

deploy-package:
	@chmod +x deploy-package.sh
	@./deploy-package.sh

deploy-all:
	@chmod +x deploy-all.sh
	@./deploy-all.sh

clean:
	@echo "Cleaning build artifacts..."
	@rm -rf build/ layer/ package/
	@echo "✓ Clean complete"
