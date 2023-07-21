
temp:
	mkdir temp

temp/0_MINES_TCE_DOE_2021_LBD.ttl: temp
	python3 scripts/1_repareCharacters.py lbd/MINES_TCE_DOE_2021_LBD.ttl temp/0_MINES_TCE_DOE_2021_LBD.ttl
	
temp/1_objects_pruned.ttl: temp/0_MINES_TCE_DOE_2021_LBD.ttl
	python3 scripts/2_pruneObjects.py temp/0_MINES_TCE_DOE_2021_LBD.ttl temp/1_objects_pruned.ttl https://ci.mines-stetienne.fr/
	
temp/2_objects_transformed.ttl: temp/1_objects_pruned.ttl
	python3 scripts/3_transformObjects.py temp/1_objects_pruned.ttl temp/2_objects_transformed.ttl https://ci.mines-stetienne.fr/

temp/3_objects_renamed.ttl: temp/2_objects_transformed.ttl
	python3 scripts/4_renameObjects.py temp/2_objects_transformed.ttl temp/3_objects_renamed.ttl https://ci.mines-stetienne.fr/
	
temp/4_schedules.ttl: temp/3_objects_renamed.ttl
	python3 scripts/5_readSchedules.py temp/3_objects_renamed.ttl temp/4_schedules.ttl https://ci.mines-stetienne.fr/

temp/5_properties.ttl: temp/4_schedules.ttl
	python3 scripts/6_addProperties.py temp/4_schedules.ttl temp/5_properties.ttl https://ci.mines-stetienne.fr/

public: temp/5_properties.ttl
	python3 scripts/7_storeTurtleFiles.py temp/5_properties.ttl  https://ci.mines-stetienne.fr/

public: temp/5_properties.ttl
	python3 scripts/8_storeHiddenLabels.py temp/5_properties.ttl  https://ci.mines-stetienne.fr/

public/emse/.htaccess: temp
	printf "DirectoryIndex index.ttl\nOptions +Indexes +MultiViews" > public/emse/.htaccess

sync:
	rsync --delete -rcv public/emse/ ci:/var/www/html/emse/
	rsync -rcv public/kg/ ci:/var/www/html/kg/