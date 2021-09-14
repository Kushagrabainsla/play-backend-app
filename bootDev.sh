envConstant="unknown"

case "$OSTYPE" in
	solaris* ) envConstant="export";;
	darwin* ) envConstant="export";;
	linux* ) envConstant="export";;
	bsd* ) envConstant="export";;
	msys* ) envConstant="set";;
	cygwin* ) envConstant="set";;
	* ) envConstant="export";;
esac

if [[ envConstant != "unknown" ]]; then
	if [[ $1 == 'dev' || $1 == 'development' ]]; then
		echo 'Development server'
		if [[ $envConstant == "set" ]]; then
			set FLASK_APP=play_backend_app
			set FLASK_ENV="development"
			flask run
		elif [[ $envConstant == "export" ]]; then
			export FLASK_APP=play_backend_app
			export FLASK_ENV="development"
			flask run
		fi

	elif [[ $1 == 'prod' || $1 == 'production' ]]; then
		echo 'Production server'
		gunicorn --worker-class eventlet -w 1 play_backend_app:app

	else
		echo "Please provide mode of running: ( dev / prod )"
	fi
else
	echo "Unknown OS, please start the server manually."
fi