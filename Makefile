build_commands = init prod
install: $(build_commands)

init:
	build-scripts/init.sh

prod: init
	build-scripts/build.sh

