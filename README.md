# Productionising dbt Core with Airflow

Welcome! 🚀

This is the repository for Astronomer's Productionising dbt Core with Airflow workshop. The workshop is designed to get you familiar with some of the main features in [Astronomer Cosmos](https://github.com/astronomer/astronomer-cosmos).

## How to use this repo

Set up your environment by following the instructions in the [Setup](#setup) section below. All DAGs in this repository can be run locally and on Astro. Given that dbt relies on running transformations on database, we are setting temporary credentials to BigQuery. These credentials will no longer work after the workshop.

Sample solutions for DAG-writing related exercises can be found in the [`solutions/`](/solutions/) folder of the repo, note that some exercises can be solved in multiple ways.

During the workshop, we encourage attendees to use the recently published eBook [Orchestrating dbt with Airflow using Cosmos](https://www.astronomer.io/ebook/orchestrating-dbt-with-airflow-using-cosmos/). You can find more examples of how to use Cosmos in the [eBook companion repository](https://github.com/astronomer/cosmos-ebook-companion).

### Setup

For this workshop, you will use a free trial of Astro to run Airflow and the Astro IDE to write dags. It is not necessary to understand all details of the Astro platform, but in a nutshell: Each customer has a dedicated Organization on Astro. One Organization can have multiple Workspaces (e.g. per team). A Workspace is a collection of Deployments. Each Workspace can have multiple Deployments. A Deployment is an Airflow environment hosted on Astro.

1. Create a free trial of Astro [using this link](https://www.astronomer.io/lp/signup/afsummit/?utm_campaign=event-airflow-summit-10-25[…]munity&utm_source=comm-evt-gen&utm_content=dbt-core-workshop).
   - After creating an account and logging in, choose `Start a Free Astro Trial` (click link Create Organization)
   - When being asked how you want to use Astro, choose Personal
   - Choose an Organization name and a Workspace name
   - When asked to select a template, click `None`. Leave all other settings and click `Create Deployment in Astro`. Note that you will not need this Deployment for this workshop, but you can use it for the remaining duration of your trial.
   - You should now see the UI of the Astro platform. Leave it for now, we'll come back to it in a few steps.
2. Install the free [Astro CLI](https://www.astronomer.io/docs/astro/cli/install-cli).
3. [Fork this repository](https://github.com/astronomer/devrel-public-workshops/fork). Make sure you uncheck the `Copy the main branch only` option when forking.

   ![Forking the repository](img/fork_repo.png)
4. Clone your fork. Get the URL by clicking on Code -> Copy to clipboard. Then run `git clone <url>`.
5. Run `git checkout dbt-in-airflow` to switch to the airflow 3 branch.
6. Ensure you are authenticated to your Astro trial by running `astro login` in your terminal. It will prompt you to go to your browser to sign in.
7. Export your project to the Astro IDE by running `astro ide project export` in your terminal. Choose `y` to create a new project, and give your project a name when prompted. Your new Astro IDE project should automatically open in a browser.
8. To start Airflow, click the `Start test deployment` button. This will create a small Airflow Deployment for you to run your dags. It may take a few minutes to spin up.
9. To enable scheduled dag runs in your new Airflow Deployment, click on the drop down next to `Sync to test`, and click `Test Deployment Details`.

   ![Test deployment details](img/deployment-change-1.png)

In the Deployment, you need to perform 2 changes:

   - Update the minimum workers by going to the `Details` tab, then `Execution` and click `Edit`.
   ![Execution](img/deployment-change-2.png)

   Set `Min # Workers` to 0, and click `Update Deployment`.
   ![Min workers](img/deployment-change-3.png)

   - Go to the `Environment` tab, click `Edit Deployment Variables`, and delete the `AIRFLOW__SCHEDULER__USE_JOB_SCHEDULE` variable.

   ![Env var](img/deployment-change-4.png)

10. Go back to the Astro IDE, and in the drop down next to `Sync to Test`, click on `Open Airflow`.
