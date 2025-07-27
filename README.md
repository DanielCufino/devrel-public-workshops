# Airflow Quickstart - Complete version

Welcome! 🚀

This is the repository for Astronomer's Airflow Quickstart. 

This quickstart contains a fully functional Airflow project for **ReLeaf**, a personalized tree recommendation service. The project demonstrates an ETL (extract-transform-load) pattern to generate tree planting recommendations for anyone from individuals to large cooperations 🌲🌳🌴!

![Screenshot of the Airflow UI showing the ETL DAG contained in this Quickstart](/img/tutorials/3-0_airflow-quickstart-etl_full_dag.png)

Optionally, you can chose to use the [workshop version](https://github.com/astronomer/devrel-public-workshops/tree/airflow-quickstart-workshop) of this quickstart with hands-on exercises to learn more about key Airflow features.

## Time to complete

This quickstart takes approximately 15 minutes to complete.

## Assumed knowledge

To get the most out of this quickstart, make sure you have an understanding of:

- Basic Airflow concepts. See [Introduction to Apache Airflow](intro-to-airflow.md).
- Basic Python. See the [Python Documentation](https://docs.python.org/3/tutorial/index.html).

## Prerequisites

- [Homebrew](https://brew.sh/) installed on your local machine. 
- An integrated development environment (IDE) for Python development, such as [Visual Studio Code](https://code.visualstudio.com/).
- (Optional) A local installation of [Python 3](https://www.python.org/downloads/) to improve your Python developer experience.

## Step 1: Install the Astro CLI

The free Astro CLI is the easiest way to run Airflow locally in a containerized environment. Follow the instructions in this step to install the Astro CLI on a Mac using [Homebrew](https://brew.sh/), for other installation options and operating systems see [Install the Astro CLI](https://www.astronomer.io/docs/astro/cli/install-cli).

1. Run the following command in your terminal to install the Astro CLI.

	```sh
	brew install astro
	```

2. Verify the installation and check your Astro CLI version. You need to be at least on version **1.34.0** to run the quickstart. 

	```sh
	astro version
	```

3. (Optional). Upgrade the Astro CLI to the latest version.

	```sh
	brew upgrade astro
	```

> [!NOTE]
> If you can't install the Astro CLI locally, skip to [Run the quickstart without the Astro CLI](#run-the-quickstart-without-the-astro-cli) to deploy and run the project with a [free trial of Astro](https://www.astronomer.io/lp/signup/?utm_source=website&utm_medium=learn-guides&utm_campaign=quickstart-etl-7-25) or use [GitHub codespaces](#run-the-quickstart-using-github-codespaces).

## Step 2: Clone and open the project

1. [Clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) the quickstart code from its [branch on GitHub](https://github.com/astronomer/devrel-public-workshops). This command will create a folder called `devrel-public-workshops` on your computer.

	```sh
	git clone -b airflow-quickstart-complete --single-branch https://github.com/astronomer/devrel-public-workshops.git
	```

2. Open the project folder in your IDE of choice. You should see the files and folders that make up your Airflow project in the file browser to the right (1). Open a terminal within your IDE by clicking on **Terminal** and then **New Terminal** (2) (if you are using [Visual Studio Code](https://code.visualstudio.com/) or [Cursor](https://cursor.com/), the default shortcut to open a terminal is Control + Shift + ```). The terminal should open at the bottom of the window (3).

	![Screenshot of the Cursor interface having opened the quickstart repository](/img/tutorials/3-0_airflow-quickstart-etl_cursor.png)

> [!TIP]
> If you quickly need a new Astro CLI project in the future you can always create one in any empty directory by running `astro dev init`.

## Step 3: Start the project

The code you cloned from GitHub already contains a fully functional Airflow project! Let's start it!


1. Run the following command in the terminal within your IDE to start the quickstart:

	```sh
	astro dev start
	```

2. As soon as the starting process is complete, the Airflow UI opens in your default browser. As long as the Airflow project is running, your can access it in another browser or additional tab by going to `localhost:8080`.

	![Airflow UI home screen](/img/tutorials/3-0_airflow-quickstart-etl_home_screen.png)

3. Click on the **Dags** button (1) in the Airflow UI to get to the DAG overview page to see the DAGs contained in this project. 

## Step 4: Run the setup DAG

You can now see the 3 DAGs in this project, they are all paused with no runs yet. To setup up the database used in the ETL DAG you can run the `releaf_database_setup` DAG. 

1. Click on the play button (2) of the `releaf_database_setup` DAG (1) to open the DAG Trigger form.

	![Screenshot of the Airflow UI showing the Dags overview with 3 paused DAGs](/img/tutorials/3-0_airflow-quickstart-etl_dags_overview.png)

	Note that there is an Import Error (3) for a fourth DAG. This DAG performs a call to a Large Language Model (LLM) to generate personalized messages based on a tree recommendation and needs a little bit more setup to use. See the [Airflow Quickstart - GenAI](airflow-quickstart-genai.md) for instructions. For now you don't have to worry about this import error it does not affect the DAGs needed for this Quickstart.

2. On the DAG Trigger form, make sure that **Single Run** (1) is selected and the Checkbox for **Unpause releaf_database_setup on trigger** is checked (2). Then click on the blue **Trigger** button (3) to create a DAG run.

	![Screenshot of the Airflow UI showing the DAG Trigger form](/img/tutorials/3-0_airflow-quickstart-etl_trigger_form.png)

3. After a few seconds the DAG run should be complete and you'll see a dark green bar in the Airflow UI for the successful DAG run (1). 

	![Screenshot of the Airflow UI showing Dags overview with 1 successful run of the releaf_database_setup DAG](/img/tutorials/3-0_airflow-quickstart-etl_succssful_run.png)

	In your IDE you can open the include folder (1) see that a new file was created, the `releaf.db` [DuckDB](https://duckdb.org/) database (2). 

	![Screenshot of Cursor showing where to see the duckdb file.](/img/tutorials/3-0_airflow-quickstart-etl_cursor_with_db.png)

## Step 5: Run the ETL DAGs

The `releaf_database_setup` DAG created the `releaf.db` and filled it with some sample data. Now it is time for you to run the ETL pipeline consisting of two DAGs `etl_releaf`, which loads an additional record to the database with tree recommendations for you, and the `releaf_analytics` DAG which summarizes the database contents.

These two DAGs depend on each other using an [Airflow Asset](airflow-datasets.md). Which means as soon as a specific task in the first DAG (`etl_releaf`) completes successfully, the second DAG `releaf_analytics` will run.

1. Unpause both DAGs by clicking their pause toggle to turn them blue (1 and 2). Unpaused DAGs will run on their defined [schedule](scheduling-in-airflow.md), which can be time-based (for example run once per day at midnight UTC) or data-aware like in this example. Next, open the DAG trigger form for the `etl_releaf` DAG by clicking on its play button (3).

	![Screenshot of the Airflow UI showing Dags overview with all DAGs unpaused](/img/tutorials/3-0_airflow-quickstart-etl_trigger_etl_dag.png)

2. The `etl_releaf` DAG runs with [params](airflow-params.md). If the DAG runs based on its schedule the given defaults are used in the code, but on a manual run, like right now, you can provide your own values. Enter your name (1) and your location (2), then trigger (3) a DAG run.

	![Screenshot of the Airflow UI showing the DAG Trigger form](/img/tutorials/3-0_airflow-quickstart-etl_trigger_form_etl_dag.png)

3. After 10-20 seconds both, the `etl_releaf` and the `releaf_analytics` DAG have completed one successful one.

	![Screenshot of the Airflow UI with successful DAG runs](/img/tutorials/3-0_airflow-quickstart-etl_succssful_run_all_three_dags.png)

## Step 6: Explore the ETL DAG

Let's explore the ETL DAG in more detail.

1. Click on the DAG name (3 in screenshot of step 5.3) to get to the DAG overview. From here you can access a lot of detailed information about this specific DAG. 

	![Screenshot of the Airflow UI showing the Grid view](/img/tutorials/3-0_airflow-quickstart-etl_dag_overview.png)

2. To navigate to the logs of individual task instance you can click on the squares in the grid view. Open the logs for the `summarize_onboarding` task to see your tree recommendations!
3. Next, to view the dependencies between your DAGs your can toggle between the **Grid** and **Graph** view in the top left corner of the DAG overview (2). Each node in the graph corresponds to one task. The edges between the nodes denote how the tasks depend on each other, by default the DAG graph is read from left to right. 

	![Screenshot of the Graph view of a DAG.](/img/tutorials/3-0_airflow-quickstart-etl_dag_graph.png)

	In the screenshot above you can see the graph of the ETL DAG, it consists of 6 tasks:

	- `extract_user_data`: This task extracts user data. In this quickstart example the DAG uses the data entered in the DAG Trigger form, the name and location of one user. In a real-world use case it would likely extract several users' records at the same time through calling an API or reading from a database.
	- `transform_user_data`: This task uses the data the first task extracted and creates a comprehensive user record from it using modularized functions stored in the `include` folder.
	- `generate_tree_recommendations`: The third task generates the tree recommendations based on the transformed data about the user.
	- `check_tables_exist`: Before loading data into the database, this tasks makes sure that the needed tables exist in the database.
	- `load_user_data`: This task loads data into the database, it can only run after both `generate_tree_recommendations` and `check_tables_exist` have completed successfully.
	- `summarize_onboarding`: The final task summarizes the data that was just loaded to the database and prints it to the logs.

4. Lastly, let's check out the code that defines this DAG by clicking on the Code tab (1). Note that while you can view the DAG code in the Airflow UI, you can only make changes to it in your IDE, not directly in the UI. You can see how each task in your DAG corresponds to one function that has been turned into an Airflow task using the [`@task` decorator](airflow-decorators.md). This one several options Airflow offers you to define your DAGs, two other common options are [traditional operators](what-is-an-operator.md) and the [`@asset` decorator](airflow-datasets.md#asset-syntax), which was used to define the `releaf_analytics` DAG. 

5. (Optional). Make a small change to your DAG code, for example by adding a print statement in one of the `@task` decorated functions. After the change has taken effect, run your DAG again and see the view the added print statement in the task logs.

> [!TIP]
> When running Airflow with default settings, it can take up to 30 seconds for DAG changes to be visible in the UI and up to 5 minutes for a new DAG (with a new DAG ID) to show up in the UI. If you don't want to wait your can run the following command to parse all existing and new DAG files in your `dags` folder.

> ```sh
> astro dev run dags reserialize
> ```

## Step 7: Deploy your project

It is time to move the project to production!

1. If you don't have access to Astro already, sign up for a free [Astro trial](https://www.astronomer.io/lp/signup/?utm_source=website&utm_medium=learn-guides&utm_campaign=quickstart-etl-7-25). 

2. [Create a new Deployment](https://www.astronomer.io/docs/astro/create-deployment) in your Astro workspace.

3. Run the following command in your local CLI to authenticate your computer to Astro. Follow the login instructions in the window that opens in your browser.

	```sh
	astro login
	```

4. Run the command to the deploy to Astro.

	```sh
	astro deploy -f
	```

5. Once the deploy has completed, click the blue `Open Airflow` button on your Deployment to see the DAGs running in the cloud. Unpause all 3 DAGs in your Astro environment and run the `releaf_database_setup` DAG manually. This will trigger a run of all 3 DAGs since they depend on each other using an `Asset` schedule.

## Next steps

Awesome! You an ETL pipeline locally and in the cloud. To continue your learning we recommend the following resources:

- If you are curious about the DAG currently showing as an import error and GenAI workflows in general, check out the [Airflow quickstart GenAI](airflow-quickstart-genai.md).
- To get a structured video-based introduction to Apache Airflow and its concepts, sign up for the [Airflow 101 (Airflow 3) Learning Path](https://academy.astronomer.io/path/airflow-101) in the Astronomer Academy.
- For a short step-by-step walkthrough of the most important Airflow features, complete our [Airflow tutorial](get-started-with-airflow.md).

## Other ways to run this quickstart

### Run the quickstart without the Astro CLI

If you cannot install the Astro CLI on your local computer you can still run the pipeline in this example.

1. Sign up for a free trial of [Astro](https://www.astronomer.io/lp/signup/?utm_source=website&utm_medium=learn-guides&utm_campaign=quickstart-etl-7-25).
2. [Create a new Deployment](https://www.astronomer.io/docs/astro/create-deployment) in your Astro workspace.
3. [Fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) the [Airflow quickstart](https://github.com/astronomer/devrel-public-workshops) repository to your GitHub account. Make sure to **uncheck** the `Copy the main branch only` box!
4. [Set up the Astro GitHub integration](https://www.astronomer.io/docs/astro/deploy-github-integration/) to map your Deployment to the `airflow-quickstart-complete` branch of your forked repository.
5. Select **Trigger Git Deploy** from the **More actions** menu in your Deployment settings to trigger the first deploy for the mapped repository.

	![Screenshot of the Astro UI showing how to Trigger a Git Deploy](/img/tutorials/3-0_airflow-quickstart-etl_astro.png)

6. Once the deploy has completed, click the blue `Open Airflow` button on your Deployment to see the DAGs running in the cloud. From here you can jump back to [Step 4](#step-4-run-the-setup-dag) and complete the quickstart up to and including [Step 6](#step-6-explore-the-etl-dag).

### Run the quickstart using GitHub Codespaces

If you can't install the CLI, you can run the project from your forked repo using GitHub Codespaces.

1. Fork this repository. Make sure you uncheck the `Copy the main branch only` option when forking.

   ![Forking the repository](img/fork_repo.png)

2. Make sure you are on the `intro-to-airflow-astro` branch.
3. Click on the green "Code" button and select the "Codespaces" tab. 
4. Click on the 3 dots and then `+ New with options...` to create a new Codespace with a configuration, make sure to select a Machine type of at least `4-core`.

   ![Start GH Codespaces](img/start_codespaces.png)

5. (Optional). If you want to be able to run the `genai_releaf` DAG that uses OpenAI to generate a message, you need to provide your own `OPENAI_API_KEY`. Add a file called `.env` in the root of your repository and enter `OPENAI_API_KEY="<your OpenAI API KEY>"`.

6. Run `astro dev start -n --wait 5m` in the Codespaces terminal to start the Airflow environment using the Astro CLI. This can take a few minutes.

   ![Start the Astro CLI in Codespaces](img/codespaces_start_astro.png)

   Once you see the following printed to your terminal, the Airflow environment is ready to use:

   ```text
   ✔ Project image has been updated
   ✔ Project started
   ➤ Airflow UI: http://localhost:8080
   ➤ Postgres Database: postgresql://localhost:5435/postgres
   ➤ The default Postgres DB credentials are: postgres:postgres
   ```

7. Once the Airflow project has started, access the Airflow UI by clicking on the Ports tab and opening the forward URL for port `8080`.

8. Run the `releaf_database_setup` DAG to create your database and populate it with sample data.

> [!TIP]
> If, when accessing the forward URL, you get an error like `{"detail":"Invalid or unsafe next URL"}`, you will need to modify the forwarded URL. Delete everything forward of `next=....` (this should be after `/login?`). The URL will update. After the URL has updated, remove `:8080`, so your URL ends in `.app.github.dev`. Now you should be able to access it.

7. It is possible that instead of the Airflow UI you see an error, in this case you have to open the URL again from the ports tab.