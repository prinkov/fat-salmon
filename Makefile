NODE_IMAGE = node:18
FRONTEND_DIR = $(PWD)/frontend

build-frontend:
	docker run --rm -it \
		-v "$(FRONTEND_DIR)":/app \
		-w /app \
		$(NODE_IMAGE) bash -c "npm install && npm run build && npm run export"

clean-frontend:
	rm -rf $(FRONTEND_DIR)/out

rebuild-frontend: clean-frontend build-frontend

dev-frontend:
	docker run --rm -it \
		-v "$(FRONTEND_DIR)":/app \
		-w /app \
		-p 3000:3000 \
		$(NODE_IMAGE) bash -c "npm install && npm run dev"
