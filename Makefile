server_install:
	sudo apt -y upgrade
	sudo apt -y install python3-pip  # Install Python
	pip install poetry  # Install Poetry
	poetry install  # Install the app dependencies in our pyproject.toml file (recall we use this instead of a requirements.txt)
	sudo apt -y install nginx  # Install nginx
	sudo cp nginx/default.conf /etc/nginx/sites-available/fastapi_app  # Copy the nginx config
	# Disable the NGINX’s default configuration file by removing its symlink
	sudo unlink /etc/nginx/sites-enabled/default
	sudo ln -s /etc/nginx/sites-available/fastapi_app /etc/nginx/sites-enabled/
