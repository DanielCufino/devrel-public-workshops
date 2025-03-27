# DAG Writing Best Practices Exercises

Welcome! 🚀

This is the repository for the Astronomer Discover Airflow 3 hands-on workshop. The workshop is designed to get you familiar with some of the biggest new features in Airflow 3.0.


## How to use this repo

Set up your environment by following the instructions in the [Setup](#setup) section below. All DAGs in this repository can be run locally and on Astro without connecting to external systems. [ADD CONTEXT ABOUT EXERCISES] If you do not have an Astro account yet, you can sign up for a free trial [here](http://q-r.to/dag-workshop-astro-trial).

Sample solutions for DAG-writing related exercises can be found in the [`dags/solutions`](/solutions/) folder of the repo, note that some exercises can be solved in multiple ways.

> [!TIP]
> Consider using [Ask Astro](ask.astronomer.io) if you need additional guidance with any of the exercises.

For additional Airflow 3.0 examples, see our repo [ADD LINK HERE].

### Setup

To set up a local Airflow environment you have two options, you can either use the Astro CLI or GitHub Codespaces.

#### Option 1: Astro CLI

1. Make sure you have [Docker](https://docs.docker.com/get-docker/) or Podman installed and running on your machine.
2. Install the free and open-source [Astro CLI](https://www.astronomer.io/docs/astro/cli/install-cli).
3. Fork this repository and clone it to your local machine. Make sure you uncheck the `Copy the main branch only` option when forking.

   ![Forking the repository](img/fork_repo.png)

4. Run `astro dev start` in the root of the cloned repository to start the Airflow environment.
5. Access the Airflow UI at `localhost:8080` in your browser. Log in using `admin` as both the username and password.

#### Option 2: GitHub Codespaces

If you can't install the CLI, you can run the project from your forked repo using GitHub Codespaces.

1. Fork this repository. Make sure you uncheck the `Copy the main branch only` option when forking.

   ![Forking the repository](img/fork_repo.png)

2. Make sure you are on the `dag-writing-best-practices` branch.
3. Click on the green "Code" button and select the "Codespaces" tab. 
4. Click on the 3 dots and then `+ New with options...` to create a new Codespace with a configuration, make sure to select a Machine type of at least `4-core`.

   ![Start GH Codespaces](img/start_codespaces.png)

5. Run `astro dev start -n --wait 5m` in the Codespaces terminal to start the Airflow environment using the Astro CLI. This can take a few minutes.

   ![Start the Astro CLI in Codespaces](img/codespaces_start_astro.png)

   Once you see the following printed to your terminal, the Airflow environment is ready to use:

   ```text
   Airflow is starting up!

   Project is running! All components are now available.

   Airflow Webserver: http://localhost:8080
   Postgres Database: localhost:5435/postgres
   The default Airflow UI credentials are: admin:admin
   The default Postgres DB credentials are: postgres:postgres
   ```

6. Once the Airflow project has started, access the Airflow UI by clicking on the Ports tab and opening the forward URL for port `8080`.
7. Log into the Airflow UI using `admin` as both the username and password. It is possible that after logging in you see an error, in this case you have to open the URL again from the ports tab.

# Exercises

## Explore the new UI

## Assets

## Backfills

## DAG versioning
