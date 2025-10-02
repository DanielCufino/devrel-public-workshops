# Airflow 3 Workshop

Welcome! 🚀

This is the repository for Astronomer's Discover Airflow 3 hands-on workshop. The workshop is designed to get you familiar with some of the biggest new features in Airflow 3.X.


## How to use this repo

Set up your environment by following the instructions in the [Setup](#setup) section below. All DAGs in this repository can be run locally and on Astro without connecting to external systems. The exercises are designed to get you exposure to new features in Airflow 3. There are also optional exercises that require an AWS account.

Sample solutions for DAG-writing related exercises can be found in the [`solutions/`](/solutions/) folder of the repo, note that some exercises can be solved in multiple ways.

For additional Airflow 3.X examples, see [our repo](https://github.com/astronomer/airflow-3-demos).

### Setup

For this workshop, you will use a free trial of Astro to run Airflow and the Astro IDE to write dags. It is not necessary to understand all details of the Astro platform, but in a nutshell: Each customer has a dedicated Organization on Astro. One Organization can have multiple Workspaces (e.g. per team). A Workspace is a collection of Deployments. Each Workspace can have multiple Deployments. A Deployment is an Airflow environment hosted on Astro.

1. Create a free trial of Astro. The host of your workshop will provide a link for you to use to create the trial.
   - After creating an account and logging in, choose `Start a Free Astro Trial` (click link Create Organization)
   - When being asked how you want to use Astro, choose Personal
   - Choose an Organization name and a Workspace name
   - When asked to select a template, click `None`. Leave all other settings and click `Create Deployment in Astro`. Note that you will not need this Deployment for this workshop, but you can use it for the remaining duration of your trial.
   - You should now see the UI of the Astro platform. Leave it for now, we'll come back to it in a few steps.
2. Install the free [Astro CLI](https://www.astronomer.io/docs/astro/cli/install-cli).
3. [Fork this repository](https://github.com/astronomer/devrel-public-workshops/fork). Make sure you uncheck the `Copy the main branch only` option when forking.

   ![Forking the repository](img/fork_repo.png)

4. Clone your fork. Get the URL by clicking on Code -> Copy to clipboard. Then run git clone <url>.
5. Run `git checkout airflow-3-ide` to switch to the airflow 3 branch.
6. Ensure you are authenticated to your Astro trial by running `astro login` in your terminal. It will prompt you to go to your browser to sign in.
7. Export your project to the Astro IDE by running `astro ide project export` in your terminal. Choose `y` to create a new project, and give your project a name when prompted. Your new Astro IDE project should automatically open in a browser.
8. To start Airflow, click the `Start test deployment` button. This will create a small Airflow Deployment for you to run your dags. It may take a few minutes to spin up.
9. To enable scheduled dag runs in your new Airflow Deployment, click on the drop down next to `Sync to test`, and click `Test Deployment Details`. In the details tab, you need to perform 2 changes:
   - Update the minimum workers by going to the `Execution` tab and clicking `Edit`. Set `Min # Workers` to 0, and click `Update Deployment`.
   - Go to the `Environment` tab, click `Edit Deployment Variables`, and delete the `AIRFLOW__SCHEDULER__USE_JOB_SCHEDULE` variable.
10. Go back to the Astro IDE, and in the drop down next to `Sync to Test`, click on `Open Airflow`.


# Exercises

The use case for this workshop is using Airflow to create an automated personalized newsletter. There is an ETL pipeline for retrieving the data, formatting it, and creating the newsletter template. Then there is another pipeline that personalizes the newsletter based on user input. The personalization pipeline is simplified to not require access to external systems - but there is a more complex GenAI version (used in the future work Exercise 7) that shows inference execution with event-driven scheduling and LLM-driven personalization. This exercise requires an AWS account with access to SQS and Bedrock to complete.

![Demo architecture diagram](img/etl_genai_newsletter_architecture_diagram_bedrock.png)

Exercises in this workshop require updating the DAGs in the `dags/` folder of this repo, and focus on newly added features in Airflow 3.

## Exercise 1: Explore the new UI

Airflow 3 has a completely refreshed UI that is React-based and easier to navigate. Once you have started Airflow, explore the new UI to develop your workflow. For more background on the Airflow UI, see [An Introduction to the Airflow UI](https://www.astronomer.io/docs/learn/airflow-ui/).

1. Review the new Home page. There won't be much here to start, but you'll change that momentarily!
2. Explore the Dags and Assets tabs. See if you can get an understanding of the relationship between the DAGs in the environment so far. What dependencies currently exist?
3. Unpause the `raw_zen_quotes` and `selected_quotes` DAGs. Run the `raw_zen_quotes` DAG, either by triggering the DAG, or creating an asset event. Is there a difference between the two methods?
4. Note what happens after `raw_zen_quotes` has run. Do any other DAGs run?
5. Try unpausing the `personalize_newsletter` DAG. It should run automatically once, but it will fail. The failure is expected, and you will fix it in the next exercise. The Airflow 3 UI makes it easier to navigate to task logs. See if you can figure out what went wrong with `personalize_newsletter`.
6. Switch between light mode and dark mode 😎
7. Try a different language from the `User` menu.


## Exercise 2: Use Assets

In the previous exercise, you explored the UI and saw that in your current Airflow environment, you have three DAGs, and three assets (`raw_zen_quotes`, `selected_quotes`, and `personalized_newsletters`). Conceptually, assets are the next evolution of Airflow datasets: they represent a collection of logically related data. You can have asset-oriented DAGs (`raw_zen_quotes`, `selected_quotes`), or task-oriented DAGs (`personalize_newsletter`). Every asset you define will create one DAG, but tasks can still produce assets and task-oriented DAGs can be scheduled on asset updates.

In this repo, `raw_zen_quotes` and `selected_quotes` are part of an asset-oriented ETL pipeline that create the general newsletter template by retrieving data from an API, formatting the data, and bringing the data together in the template. You'll notice that the "load" step to bring the template together is missing. Let's fix that. For more background on assets, see [Assets and Data-Aware Scheduling in Airflow](https://www.astronomer.io/docs/learn/airflow-datasets/).

1. Go back to the Astro IDE, and open the `create_newsletter.py` file in the code editor.

2. Create a new asset in `create_newsletter.py` called `formatted_newsletter`. Use the following Python code as the _body_ of the asset:
```python
"""
Formats the newsletter.
"""
from airflow.io.path import ObjectStoragePath

object_storage_path = ObjectStoragePath(
   f"{OBJECT_STORAGE_SYSTEM}://{OBJECT_STORAGE_PATH_NEWSLETTER}",
   conn_id=OBJECT_STORAGE_CONN_ID,
)

selected_quotes = context["ti"].xcom_pull(
      dag_id="selected_quotes",
      task_ids=["selected_quotes"],
      key="return_value",
      include_prior_dates=True,
   )[0]

# fetch the run date of the pipeline
run_date = context["triggering_asset_events"][Asset("selected_quotes")][0].extra[
   "run_date"
]

newsletter_template_path = object_storage_path / "newsletter_template.txt"

newsletter_template = newsletter_template_path.read_text()

newsletter = newsletter_template.format(
   quote_text_1=selected_quotes["short_q"]["q"],
   quote_author_1=selected_quotes["short_q"]["a"],
   quote_text_2=selected_quotes["median_q"]["q"],
   quote_author_2=selected_quotes["median_q"]["a"],
   quote_text_3=selected_quotes["long_q"]["q"],
   quote_author_3=selected_quotes["long_q"]["a"],
   date=run_date,
)

date_newsletter_path = object_storage_path / f"{run_date}_newsletter.txt"

date_newsletter_path.write_text(newsletter)

# attach the run date to the asset event
yield Metadata(Asset("formatted_newsletter"), {"run_date": run_date})
```

3. Give the asset a schedule. It should run when the `selected_quotes` asset is available.
4. After you have saved the file, check out your new asset graph in the Airflow UI. You should see your full ETL pipeline with three DAGs and three assets.
5. Now that your ETL pipeline is complete, take a look at the `personalize_newsletter` DAG. This DAG is currently set to run daily, but it will actually fail if the `formatted_newsletter` asset has not been updated. Change the schedule of `personalize_newsletter` so that it actually runs only when the right data is available.
6. This pipeline will generate a newsletter with motivational quotes and personalized weather information. In the `include/user_data` folder, update `user_100.json` to include your own name and location.
   - Bonus: try adding additional user files in `include/user_data` and see how that changes the pipeline when it runs.
7. Deploy your changes by clicking `Sync to Test` in the upper right. This will send the changes you made to your two dags to your test Deployment. Note that syncing may take a few minutes.
8. To ensure your changes were made, use the reparse dag function in the UI for the `personalize_newsletter` dag. Then, run your full pipeline by materializing the `raw_zen_quotes` DAG. This should trigger all downstream assets and tasks to complete.

> [!TIP]
> The open-meteo weather API is occasionally flaky. If you get a failure in your `get_weather_info` task, let it retry, it will usually resolve. If you added additional users, you may need to implement a pool so you don't hit API rate limits. Ask one of your workshop leaders for help with this.

## Exercise 3: Add a human-in-the-loop

Airflow 3.1 introduced human-in-the-loop (HITL) operators, which allow you to manually intervene in your dags mid-dag run. In this use case, you might want a human to review the results of the newsletter personalization before sending. For more on HITL, see [Human-in-the-loop workflows with Airflow](https://www.astronomer.io/docs/learn/airflow-human-in-the-loop).

1. In the Astro IDE code editor, open the `personalize_newsletter.py` file.
2. Add a HITL operator to this dag that approves or rejects the output of the `get_weather_info` task. It should look like this:

   ```python
   approve_personalization = ApprovalOperator(
      task_id="approve_personalization",
      subject="Your task:",
      body="{{ ti.xcom_pull(task_ids='get_weather_info') }}",
      defaults="Approve", # other option: "Reject"
    )
   ```

3. Make sure to also adjust the task dependencies in the dag, so that this task comes after `get_weather_info` but before `create_personalized_newsletter`.
4. Deploy your changes by clicking `Sync to Test` in the upper right. This will send the changes you made to your two dags to your test Deployment. Note that syncing may take a few minutes.
5. Run the `personalize_newsletter` dag again, and approve (or reject!) the results of your newsletter personalization by reviewing the `Required Actions` from your HITL operator.


## Exercise 4: Run a Backfill

For ETL pipelines that are time-dependent, like this one in this example, you may occasionally need to reprocess historical data. Backfills are a first-class feature in Airflow 3, and make this easy. For more info on backfills, see [Rerun Airflow DAGs and Tasks](https://www.astronomer.io/docs/learn/rerunning-dags/).

Let's say you just deployed these pipelines, and you need to create newsletters for the past couple of days.

1. Start a backfill of the `raw_zen_quotes` DAG using the UI, by clicking the blue `Trigger` button and selecting `Backfill`. (see: [Backfill](https://www.astronomer.io/docs/learn/rerunning-dags#backfill))
2. In the `Backfill` form, choose a date range and reprocessing behavior for your backfill. The form will show you how many runs will be triggered based on your selections. See if you can select setting that will trigger 2 dag runs.
3. Start the backfill, and notice the progress bar in the UI (you may need to refresh the page). What is different about these runs in the grid?
4. Notice what happened to the other downstream DAGs in your environment. Were they triggered as well? 
5. You might notice that with the HITL operator we added, you have to interact with the reprocessed runs. Try out the instance-wide view for HITL via Browse -> Required Actions.

## Exercise 6: Use DAG versioning

DAG versioning is a new feature in Airflow 3 that allows you to track changes to your DAG code over time in the Airflow UI. DAG versioning using the `LocalDagBundle` is set up automatically. For more background on dag versioning, see [DAG Versioning and DAG Bundles](https://www.astronomer.io/docs/learn/airflow-dag-versioning/).

Changes to your DAG's structure will prompt a new version to be recorded by Airflow. In Exercises 2 and 3, you made changes to the `personalize_newsletter` dag - let's start there. 

1. In the Airflow UI, go to the Graph of your `personalize_newsletter` DAG, click on `Options` and notice the Dag Version drop down. How many versions are there?
2. Toggle the graph between the different versions. You should see changes in the graph for when you added a new task.
3. Go to the Code tab and try toggling the different versions there, so you can see how the code has changed with each version.

> [!TIP]
> New DAG versions are only created when the DAG's structure changes since the last run. Making a change to the task code will not prompt a new version.


## (Future work) Exercise 7: Run a GenAI DAG with event-driven scheduling

The `personalize_newsletter` pipeline in this workshop is designed to not require connections to any external systems. While this is helpful for workshop participants who may not all use the same tech stack, it is not representative of real-world Airflow usage.

To demonstrate a more realistic version of this pipeline, we have also included a version that personalizes the newsletter quotes by sending user input to an LLM through Amazon Bedrock, and runs when a message arrives in SQS. This simulates event-driven scheduling, that you might expect if you offered an on-demand newsletter to customers - so your pipeline runs as soon as users input their information. For more on event-driven scheduling, see [Event-Driven Scheduling](https://www.astronomer.io/docs/learn/airflow-event-driven-scheduling/).

You can run this version of the pipeline yourself if you have access to an AWS account:

1. Replace the contents of `dags/personalize_newsletter.py` with the code in `solutions/personalize_newsletter_genai.py` (this will create a new DAG version!). 
2. Add the contents of `.env_example` to `.env`, making sure to update `AIRFLOW_CONN_AWS_DEFAULT` with the credentials for your AWS account. If you do this, MAKE SURE to add the `.env` file to `.gitignore` so you do not push your credentials to GitHub.
3. Create a new SQS queue, and add the URL to `SQS_QUEUE_URL` in your `.env` file.
4. Restart your Airflow project with `astro dev restart` for the `.env` changes to take effect.
5. Run the new `personalize_newsletter` DAG by adding a message to your SQS queue with the following format:
   ```
   {
    "id": 300,
    "name": "Kenten",
    "location": "Seattle",
    "motivation": "Finding my way.",
    "favorite_sci_fi_character": "Spock (Star Trek)"
   }
   ```
6. Check to see that your `personalize_newsletter` DAG started running. Note that you can change the Bedrock model used by the DAG, and you may need to request access to a particular model from within your AWS account if you have not already used it.
7. Review your personalized newsletter in `include/newsletters`.

