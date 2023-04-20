server_install:
	sudo apt -y upgrade
	sudo apt -y install python3-pip  # Install Python
	pip install poetry  # Install Poetry
	poetry install  # Install the app dependencies in our pyproject.toml file (recall we use this instead of a requirements.txt)
	sudo apt -y install nginx supervisor # Install nginx
	sudo systemctl enable supervisor
	sudo systemctl start supervisor
