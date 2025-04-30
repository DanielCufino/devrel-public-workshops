# Airflow 3 Workshop

Welcome! 🚀

This is the repository for Astronomer's Discover Airflow 3 hands-on workshop. The workshop is designed to get you familiar with some of the biggest new features in Airflow 3.0.


## How to use this repo

Set up your environment by following the instructions in the [Setup](#setup) section below. All DAGs in this repository can be run locally and on Astro without connecting to external systems. The exercises are designed to get you exposure to new features in Airflow 3. There are also optional exercises that require an AWS account.

Sample solutions for DAG-writing related exercises can be found in the [`dags/solutions`](/solutions/) folder of the repo, note that some exercises can be solved in multiple ways.

> [!TIP]
> Consider using [Ask Astro](ask.astronomer.io) if you need additional guidance with any of the exercises.

For additional Airflow 3.0 examples, see (our repo)[https://github.com/astronomer/airflow-3-demos].

### Setup

To set up a local Airflow environment you have two options, you can either use the Astro CLI or GitHub Codespaces.

#### Option 1: Astro CLI

1. Make sure you have [Docker](https://docs.docker.com/get-docker/) or Podman installed and running on your machine.
2. Install the free [Astro CLI](https://www.astronomer.io/docs/astro/cli/install-cli).
3. Fork this repository and clone it to your local machine. Make sure you uncheck the `Copy the main branch only` option when forking.

   ![Forking the repository](img/fork_repo.png)

4. Run `astro dev start` in the root of the cloned repository to start the Airflow environment.
5. Access the Airflow UI at `localhost:8080` in your browser. Log in using `admin` as both the username and password.

#### Option 2: GitHub Codespaces

If you can't install the CLI, you can run the project from your forked repo using GitHub Codespaces.

1. Fork this repository. Make sure you uncheck the `Copy the main branch only` option when forking.

   ![Forking the repository](img/fork_repo.png)

2. Make sure you are on the `airflow-3-0` branch.
3. Click on the green "Code" button and select the "Codespaces" tab. 
4. Click on the 3 dots and then `+ New with options...` to create a new Codespace with a configuration, make sure to select a Machine type of at least `4-core`.

   ![Start GH Codespaces](img/start_codespaces.png)

5. Run `astro dev start -n --wait 5m` in the Codespaces terminal to start the Airflow environment using the Astro CLI. This can take a few minutes.

   ![Start the Astro CLI in Codespaces](img/codespaces_start_astro.png)

   Once you see the following printed to your terminal, the Airflow environment is ready to use:

   ```text
   ✔ Project started
   ➤ Airflow Webserver: http://localhost:8080
   ➤ Postgres Database: postgresql://localhost:5435/postgres
   ➤ The default Airflow UI credentials are: admin:admin
   ➤ The default Postgres DB credentials are: postgres:postgres
   ```

6. Once the Airflow project has started, access the Airflow UI by clicking on the Ports tab and opening the forward URL for port `8080`.
7. Log into the Airflow UI using `admin` as both the username and password. It is possible that after logging in you see an error, in this case you have to open the URL again from the ports tab.

# Exercises

The use case for this workshop is using Airflow to create an automated personalized newsletter. There is an ETL pipeline for retrieving the data, formatting it, and creating the newsletter template. Then there is another pipeline that personalizes the newsletter based on user input. The personalization pipeline is simplified to not require access to external systems - but there is a more complex GenAI version (used in the optional Exercise 5) that shows inference execution with event-driven scheduling and LLM-driven personalization. This exercise requires an AWS account with access to SQS and Bedrock to complete.

ADD SCREENSHOT


Exercises in this workshop require updating the DAGs in the `dags/` folder of this repo, and focus on newly added features in Airflow 3.0. For more background on these features, use the following resources:

- [An Introduction to the Airflow UI](https://www.astronomer.io/docs/learn/airflow-ui/)
- [Assets and Data-Aware Scheduling in Airflow](https://www.astronomer.io/docs/learn/airflow-datasets/)
- [DAG Versioning and DAG Bundles](https://www.astronomer.io/docs/learn/airflow-dag-versioning/)
- [Rerun Airflow DAGs and Tasks](https://www.astronomer.io/docs/learn/rerunning-dags/)
- [Event-Driven Scheduling](https://www.astronomer.io/docs/learn/airflow-event-driven-scheduling/)


## Exercise 1: Explore the new UI

Airflow 3 has a completely refreshed UI that is React-based and easier to navigate. Once you have started Airflow, explore the new UI to develop your workflow.

1. Review the new Home page. There won't be much here to start, but you'll change that momentarily!
2. Explore the Dags and Assets tabs. See if you can get an understanding of the relationship between the DAGs in the environment so far. What dependencies currently exist?
3. Unpause all of the DAGs, then try running one. Run the `selected_quotes` DAG, either by triggering the DAG, or creating an asset event. Is there a difference between the two methods?
4. Note what happens after `selected_quotes` has run. Do any other DAGs run?
5. Switch to dark mode 😎


## Exercise 2: Use Assets

In the previous exercise, you explored the UI and saw that in your current Airflow environment, you have three DAGs, and three assets (`raw_zen_quotes`, `selected_quotes`, and `personalized_newsletters`). Conceptually, assets are the next evolution of Airflow datasets: they represent a collection of logically related data. You can have asset-oriented DAGs (`raw_zen_quotes`, `selected_quotes`), or task-oriented DAGs (`personalize_newsletter`). Every asset you define will create one DAG, but tasks can still produce assets and task-oriented DAGs can be scheduled on asset updates.

In this repo, `raw_zen_quotes` and `selected_quotes` are part of an asset-oriented ETL pipeline that create the general newsletter template by retrieving data from an API, formatting the data, and bringing the data together in the template. You'll notice that the "load" step to bring the template together is missing. Let's fix that.

1. Create a new asset in `create_newsletter.py` called `formatted_newsletter` using the following Python code:
   ```python
    """
    Formats the newsletter.
    """
    from airflow.io.path import ObjectStoragePath

    object_storage_path = ObjectStoragePath(
        f"{OBJECT_STORAGE_SYSTEM}://{OBJECT_STORAGE_PATH_NEWSLETTER}",
        conn_id=OBJECT_STORAGE_CONN_ID,
    )

    date = context["dag_run"].run_after.strftime("%Y-%m-%d")

    selected_quotes = context["ti"].xcom_pull(
        dag_id="selected_quotes",
        task_ids=["selected_quotes"],
        key="return_value",
        include_prior_dates=True,
    )

    newsletter_template_path = object_storage_path / "newsletter_template.txt"

    newsletter_template = newsletter_template_path.read_text()

    newsletter = newsletter_template.format(
        quote_text_1=selected_quotes["short_q"]["q"],
        quote_author_1=selected_quotes["short_q"]["a"],
        quote_text_2=selected_quotes["median_q"]["q"],
        quote_author_2=selected_quotes["median_q"]["a"],
        quote_text_3=selected_quotes["long_q"]["q"],
        quote_author_3=selected_quotes["long_q"]["a"],
        date=date,
    )

    date_newsletter_path = object_storage_path / f"{date}_newsletter.txt"

    date_newsletter_path.write_text(newsletter)
    ```
2. Give the asset a schedule. It should run when the `selected_quotes` asset is available.
3. After you have saved the file, check out your new asset graph in the Airflow UI. You should see your full ETL pipeline with three DAGs and three assets.
4. Now that your ETL pipeline is complete, take a look at the `personalize_newsletter` DAG. This DAG is currently set to run daily, but it will actually fail if the `formatted_newsletter` asset has not been updated. Change the schedule of `personalize_newsletter` so that it actually runs only when the right data is available.
5. This pipeline will generate a newsletter with motivational quotes and personalized weather information. In the `include/user_data` folder, update `user_100.json` to include your own name and location.
   - Bonus: try adding additional user files in `include/user_data` and see how that changes the pipeline when it runs.
6. Run your full pipeline by materializing the `raw_zen_quotes` DAG. This should trigger all downstream assets and tasks to complete. Check that everything worked by reviewing the DAG runs in the Airflow UI, and checking your local `include/newsletter` folder for your personalized newsletter.

## Exercise 3: Run a Backfill

## Exercise 4: Use DAG versioning


## (Optional) Exercise 5: Run a GenAI DAG with event-driven scheduling
