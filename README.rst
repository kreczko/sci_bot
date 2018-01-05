=========
sci_bot - Science Continuous Integration bot
=========


.. image:: https://img.shields.io/pypi/v/sci_bot.svg
        :target: https://pypi.python.org/pypi/sci_bot

.. image:: https://img.shields.io/travis/kreczko/sci_bot.svg
        :target: https://travis-ci.org/kreczko/sci_bot

.. image:: https://readthedocs.org/projects/ci-bot/badge/?version=latest
        :target: https://ci-bot.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/kreczko/sci_bot/shield.svg
     :target: https://pyup.io/repos/github/kreczko/sci_bot/
     :alt: Updates


A bot for all the Science CI needs


* Free software: Apache Software License 2.0
* Documentation: https://sci-bot.readthedocs.io.


Features
--------

* Easy setup of pipelines across multiple projects via configuration repository (TODO)
* Metric reporting and tracking (TODO)
* set of commands for manual steering (TODO)
* release validation on tagging (TODO)
* simple web frontend to forward gitlab hooks to a Kafka service (currently outside this project: kreczko/webhook_forwarder)

Docker
--------
To start the ci-bot simply run::

    docker-compose up -d
    docker exec -ti scibot_box_1 cdw



Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
