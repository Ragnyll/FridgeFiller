
FIXTURES += $(wildcard */fixtures/*.json)

FIXTURESD = $(FIXTURES:%.json=%.d)

loaddata: ${FIXTURESD}
	@echo "Data loaded!"

%.d: %.json
	python manage.py loaddata $<
	touch $@
