# Airflow Quickstart - Complete version

Welcome to Astronomer's [Apache Airflow®](https://airflow.apache.org/) ETL Quickstart! 🚀 

You will set up and run a fully functional Airflow project for **ReLeaf**, a TaaS (Trees-as-a-Service) business that provides personalized, hyperlocal recommendations for which trees to plant in an area. This quickstart contains both, an ETL (extract-transform-load) pattern and a GenAI DAG to generate tree planting recommendations for anyone from individuals to large corporations 🌲🌳🌴!

![Screenshot of the Airflow UI showing the ETL DAG contained in this Quickstart](/img/3-0_airflow-quickstart-etl_full_dag.png)

> [!TIP]
> Optionally, you can choose to use the [workshop version](https://github.com/astronomer/devrel-public-workshops/tree/airflow-quickstart-workshop) of this quickstart with hands-on exercises in the README to practice using key Airflow features.

## Time to complete

This quickstart takes approximately 25 minutes to complete.

## Assumed knowledge

To get the most out of this quickstart, make sure you have an understanding of:

- Basic Airflow concepts. See [Introduction to Apache Airflow](intro-to-airflow.md).
- Basic Python. See the [Python Documentation](https://docs.python.org/3/tutorial/index.html).

## Prerequisites

- [Homebrew](https://brew.sh/) installed on your local machine. 
- An integrated development environment (IDE) for Python development, such as [Visual Studio Code](https://code.visualstudio.com/).
- (Optional) A local installation of [Python 3](https://www.python.org/downloads/) to improve your Python developer experience.

> [!NOTE]
> If you can't install the prerequisites or the Astro CLI locally, skip to [Other ways to run the quickstart](#other-ways-to-run-this-quickstart) for information on other options to run this Airflow project.

## Step 1: Install the Astro CLI

The free Astro CLI is the easiest way to run Airflow locally in a containerized environment. Follow the instructions in this step to install the Astro CLI on a Mac using [Homebrew](https://brew.sh/), for other installation options and operating systems see [Install the Astro CLI](https://www.astronomer.io/docs/astro/cli/install-cli).

1. Run the following command in your terminal to install the Astro CLI.

	```sh
	brew install astro
	```

2. Verify the installation and check your Astro CLI version. You need to be on at least version **1.34.0** to run the quickstart. 

	```sh
	astro version
	```

3. (Optional). Upgrade the Astro CLI to the latest version.

	```sh
	brew upgrade astro
	```



## Step 2: Clone and open the project

1. [Clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) the quickstart code from its [branch on GitHub](https://github.com/astronomer/devrel-public-workshops). This command will create a folder called `devrel-public-workshops` on your computer.

	```sh
	git clone -b airflow-quickstart-complete --single-branch https://github.com/astronomer/devrel-public-workshops.git
	```

2. Open the project folder in your IDE of choice. This quickstart uses [Cursor](https://cursor.com/) which is very similar to [Visual Studio Code](https://code.visualstudio.com/). 

	You should see the files and folders that make up your Airflow project in the file browser to the right (1). Open a terminal within your IDE by clicking on **Terminal** and then **New Terminal** (2) (the default shortcut to open a terminal is Control + Shift + `). The terminal should open at the bottom of the window (3).

	![Screenshot of the Cursor IDE having opened the quickstart repository and a new terminal](/img/3-0_airflow-quickstart-etl_cursor.png)

> [!TIP]
> If you quickly need a new Airflow project in the future you can always create one in any empty directory by running `astro dev init`.


## Step 3: Add your OpenAI API Key

In order to be able to send requests to a Large Language Model (LLM) via the Airflow AI SDK you need to have an API Key and make it available to the Airflow AI SDK as an environment variable. This quickstart uses [OpenAI](https://platform.openai.com/docs/overview); you can learn about other model providers that are compatible with the Airflow AI SDK [here](https://github.com/astronomer/airflow-ai-sdk/blob/main/pyproject.toml#L30).

1. In the root of your repository, create a new file called `.env` (1). This file is ignored by git and a good place to define your (secret) environment variables

	![Screenshot of Cursor showing an added .env file for the OpenAI API Key.](/img/3-0_airflow-quickstart-genai_openai.png)

2. In the `.env` file, define a variable called `OPENAI_API_KEY` and set it to your [OpenAI API Key](https://platform.openai.com/docs/api-reference/authentication) (2). 
3. To use the AI SDK you also need to install the [Airflow AI SDK Python package](https://github.com/astronomer/airflow-ai-sdk) with the extra relevant to your model provider by adding it to the `requirements.txt` file. This has already been done for you in the quickstart repository.

> [!NOTE]
> Whenever you make changes to your `.env` or `requirements.txt` file you need to restart your Airflow environment using `astro dev restart` for the changes to take effect.


## Step 4: Start the project

The code you cloned from GitHub already contains a fully functional Airflow project! Let's start it!


1. Run the following command in the terminal within your IDE to start the quickstart:

	```sh
	astro dev start
	```

> [!NOTE]
> If port 8080 or 5432 are in use on your machine, Airflow won't be able to start. To run Airflow on alternative ports, run:

> ```sh
> astro config set webserver.port <available-port>
> astro config set postgres.port <available-port>
> ```

2. As soon as the starting process is complete, the Airflow UI opens in your default browser. When running the starting command for the first time this might take a couple of minutes. Note that, as long as the Airflow project is running, you can always access the UI in another browser or additional tab by going to `localhost:8080`. 

	![Airflow UI home screen](/img/3-0_airflow-quickstart-etl_home_screen.png)

3. Click on the **Dags** button (1) in the Airflow UI to get to the Dags overview page to see all the DAGs contained in this project. 

## Step 5: Run the setup DAG

You can now see 3 DAGs of this project, they are all paused with no runs yet. In this step you'll run the `releaf_database_setup` DAG to set up the database used in the ETL DAG in [Step 5](#step-5-run-the-etl-dags).

1. Click on the play button (2) of the `releaf_database_setup` DAG (1) to open its DAG Trigger form.

	![Screenshot of the Airflow UI showing the Dags overview with 3 paused DAGs](/img/3-0_airflow-quickstart-etl_dags_overview.png)

	Note that there is an Import Error (3) for a fourth DAG. This DAG performs a call to a Large Language Model (LLM) to generate personalized messages based on a tree recommendation and needs a little bit more setup to use. See the [Airflow Quickstart - GenAI](airflow-quickstart-genai.md) for instructions. For this ETL quickstart you don't have to worry about this import error it does not affect the DAGs in the ETL pipeline.

2. On the DAG Trigger form, make sure that **Single Run** (1) is selected and the Checkbox for **Unpause releaf_database_setup on trigger** is checked (2). Then click on the blue **Trigger** button (3) to create a DAG run.

	![Screenshot of the Airflow UI showing the DAG Trigger form](/img/3-0_airflow-quickstart-etl_trigger_form.png)

3. After a few seconds the DAG run should be complete and you'll see a dark green bar in the Airflow UI (1). 

	![Screenshot of the Airflow UI showing Dags overview with 1 successful run of the releaf_database_setup DAG](/img/3-0_airflow-quickstart-etl_succssful_run.png)

	In your IDE you can open the include folder (1) to see that a new file was created, the `releaf.db` [DuckDB](https://duckdb.org/) database (2). This is the database the ETL DAG interacts with.

	![Screenshot of Cursor showing where to see the duckdb file.](/img/3-0_airflow-quickstart-etl_cursor_with_db.png)

## Step 6: Run the ETL DAGs

The `releaf_database_setup` DAG created the `releaf.db` and filled it with some sample data. Now it is time for you to run the ETL pipeline consisting of two DAGs `etl_releaf`, which loads an additional record to the database with tree recommendations for you, and the `releaf_analytics` DAG which summarizes the database contents.

These two DAGs depend on each other using an [Airflow Asset](airflow-datasets.md), which means that as soon as a specific task in the first DAG (the `summarize_onboarding` task in the `etl_releaf` DAG) completes successfully, the second DAG (`releaf_analytics`) will run automatically.

1. Unpause both DAGs by clicking their pause toggle to turn them blue (1 and 2). Unpaused DAGs will run on their defined [schedule](scheduling-in-airflow.md), which can be time-based (for example run once per day at midnight UTC) or data-aware like in this example. Next, open the DAG trigger form for the `etl_releaf` DAG by clicking on its play button (3).

	![Screenshot of the Airflow UI showing Dags overview with all DAGs unpaused](/img/3-0_airflow-quickstart-etl_trigger_etl_dag.png)

2. The `etl_releaf` DAG runs with [params](airflow-params.md). If the DAG runs based on its schedule the given defaults are used, but on a manual run, like right now, you can provide your own values. Enter your name (1) and your location (2), then trigger (3) a DAG run.

	![Screenshot of the Airflow UI showing the DAG Trigger form](/img/3-0_airflow-quickstart-etl_trigger_form_etl_dag.png)

3. After 10-20 seconds both the `etl_releaf` and the `releaf_analytics` DAG have completed successfully (1 and 2).

	![Screenshot of the Airflow UI with successful DAG runs](/img/3-0_airflow-quickstart-etl_succssful_run_all_three_dags.png)

## Step 7: Explore the ETL DAG

Let's explore the ETL DAG in more detail.

1. Click on the DAG name (3 in screenshot of step 5.3) to get to the DAG overview. From here you can access a lot of detailed information about this specific DAG. 

	![Screenshot of the Airflow UI showing the Grid view](/img/3-0_airflow-quickstart-etl_dag_overview.png)

2. To navigate to the logs of individual task instances, click on the squares in the grid view. Open the logs for the `summarize_onboarding` task (1) to see your tree recommendations!
3. Next, to view the dependencies between your DAGs you can toggle between the **Grid** and **Graph** view in the top left corner of the DAG overview (2). Each node in the graph corresponds to one task. The edges between the nodes denote how the tasks depend on each other, and by default the DAG graph is read from left to right. 

	![Screenshot of the Graph view of a DAG.](/img/3-0_airflow-quickstart-etl_dag_graph.png)

	In the screenshot above you can see the graph of the ETL DAG, it consists of 6 tasks:

	- `extract_user_data`: This task extracts user data. In this quickstart example the DAG uses the data entered in the DAG Trigger form, the name and location of one user. In a real-world use case, it would likely extract several users' records at the same time through calling an API or reading from a database.
	- `transform_user_data`: This task uses the data the first task extracted and creates a comprehensive user record from it using modularized functions stored in the `include` folder.
	- `generate_tree_recommendations`: The third task generates the tree recommendations based on the transformed data about the user.
	- `check_tables_exist`: Before loading data into the database, this task makes sure that the needed tables exist in the database.
	- `load_user_data`: This task loads data into the database, it can only run after both `generate_tree_recommendations` and `check_tables_exist` have completed successfully.
	- `summarize_onboarding`: The final task summarizes the data that was just loaded to the database and prints it to the logs.

4. Let's check out the code that defines this DAG by clicking on the Code tab (1). Note that while you can view the DAG code in the Airflow UI, you can only make changes to it in your IDE, not directly in the UI. You can see how each task in your DAG corresponds to one function that has been turned into an Airflow task using the [`@task` decorator](airflow-decorators.md). 

> [!NOTE]
> The [`@task` decorator](airflow-decorators.md) is one of several options to define your DAGs, the two other options are using [traditional operators](what-is-an-operator.md) or the [`@asset` decorator](airflow-datasets.md#asset-syntax).

5. The second DAG in this ETL pipeline, `releaf_analytics`, is defined with the [`@asset` decorator](airflow-datasets.md#asset-syntax), a shorthand to create one DAG with one task updating one [Asset](airflow-datasets.md). 

	![Screenshot of the task logs of the releaf_analytics task showing 501 users in the database.](/img/3-0_airflow-quickstart-etl_analytics.png)

	Click on the DAG name in the DAG overview page, and then on the square for the `releaf_analytics` task (1) to view the logs containing summary analytics about your tree recommendations. Since the setup DAG adds 500 users to the database, and you just added yourself with the ETL DAG, you should see `501` users in the log output (2). Viewing the DAG code (3) you can see how the `@asset` decorator quickly turns a Python function into an Airflow DAG with one task.

6. (Optional). Make a small change to your DAG code, for example by adding a print statement in one of the `@task` decorated functions. After the change has taken effect, run your DAG again and see the added print statement in the task logs.

> [!TIP]
> When running Airflow with default settings, it can take up to 30 seconds for DAG changes to be visible in the UI and up to 5 minutes for a new DAG (with a new DAG ID) to show up in the UI. If you don't want to wait you can run the following command to parse all existing and new DAG files in your `dags` folder.
>
> ```sh
> astro dev run dags reserialize
> ```

## Step 8: Run the GenAI DAGs

Next, you will run the GenAI DAG to create a description of your future garden!

1. Open the Trigger DAG form of the `genai_releaf` DAG by clicking on its play button (1). 

	![DAGs overview showing the play button for the genai_releaf DAG.](/img/3-0_airflow-quickstart-genai_dags_overview.png)

2. The `genai_releaf` DAG runs with the same [params](airflow-params.md) as the ETL DAG. If the DAG were to run based on a schedule the given defaults are used, but on a manual run, like right now, you can provide your own values. In the Trigger DAG form, enter your name (1) and your location (2), then trigger (3) a DAG run. Make sure the **Unpause genai_releaf on trigger** checkbox (4) is selected.

	![Screenshot of the Airflow UI showing the DAG Trigger form](/img/3-0_airflow-quickstart-genai_trigger_dag.png)

3. After 20-30 seconds the `genai_releaf` DAG has completed successfully (1).

	![DAGs overview showing a successful run of the genai_releaf DAG.](/img/3-0_airflow-quickstart-genai_overview_successful_run.png)

## Step 9: Explore the GenAI DAG

Let's explore the ETL DAG in more detail.

1. Click on the DAG name (2 in screenshot of step 5.3) to get to the DAG overview. From here you can access a lot of detailed information about this specific DAG. 

	![Screenshot of the Airflow UI showing the Grid view](/img/3-0_airflow-quickstart-genai_grid.png)

2. To navigate to the logs of individual task instances, click on the squares in the grid view. Open the logs for the `print_llm_output` task (1) to see your garden description!
3. Next, to view the dependencies between your DAGs you can toggle between the **Grid** and **Graph** view in the top left corner of the DAG overview (2). Each node in the graph corresponds to one task. The edges between the nodes denote how the tasks depend on each other, and by default the DAG graph is read from left to right. 

	![Screenshot of the Graph view of a DAG.](/img/3-0_airflow-quickstart-genai_graph_view_dag.png)

	In the screenshot above you can see the graph of the ETL DAG, it consists of 6 tasks:

	- The first 3 tasks: `extract_user_data`, `transform_user_data` and `generate_tree_recommendations` are the same as in the ETL DAG. Note that this repeated code could be modularized further with the tasks fully moved to the `include` folder and only the task function call being part of the DAG file. 
	- `generate_garden_description`: This task uses the `@task.llm` decorator of the Airflow AI SDK to make a call to the OpenAI API to generate a description of your future garden, if you were to follow the tree recommendations.
	- `print_llm_output`: The final task prints the output of the LLM to the task logs.

4. Lastly, let's check out the code that defines this DAG by clicking on the Code tab (1). Remember, that while you can view the DAG code in the Airflow UI, you can only make changes to it in your IDE, not directly in the UI. You can see how each task in your DAG corresponds to one function that has been turned into an Airflow task using the [`@task` decorator](airflow-decorators.md).

## Step 10: Deploy your project

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

5. Since environment variables often contain secrets, they are not deployed from `.env` with the rest of your project code. To add environment variables like your `OPENAI_API_KEY` to an Astro Deployment, use the `Environment` tab (1) on your Deployment. Make sure to mark the environment variables as secret!

	![Astro UI showing the Environment tab.](/img/3-0_airflow-quickstart-genai_environment_astro.png)

6. Once the deploy has completed, click the blue `Open Airflow` button on your Deployment to see the DAGs running in the cloud. Here, you can run all the DAGs again, starting with the `releaf_database_setup` setup DAG.

## Next steps

Awesome! You ran both, an ETL pipeline and a GenAI DAG locally and in the cloud. To continue your learning we recommend the following resources:

- To get a structured video-based introduction to Apache Airflow and its concepts, sign up for the [Airflow 101 (Airflow 3) Learning Path](https://academy.astronomer.io/path/airflow-101) in the Astronomer Academy.
- For a short step-by-step walkthrough of the most important Airflow features, complete our [Airflow tutorial](get-started-with-airflow.md).


## Other ways to run this quickstart

### Run the quickstart on Astro without the Astro CLI

If you cannot install the Astro CLI on your local computer, you can still run the pipeline in this example.

1. Sign up for a free trial of [Astro](https://www.astronomer.io/lp/signup/?utm_source=website&utm_medium=learn-guides&utm_campaign=quickstart-etl-7-25).
2. [Create a new Deployment](https://www.astronomer.io/docs/astro/create-deployment) in your Astro workspace.
3. [Fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) the [Airflow quickstart](https://github.com/astronomer/devrel-public-workshops) repository to your GitHub account. Make sure to **uncheck** the `Copy the main branch only` box!

	![Screenshot of GitHub showing how to fork the respository and the box to uncheck](/img/3-0-airflow-quickstart-etl_fork_repo.png)

4. [Set up the Astro GitHub integration](https://www.astronomer.io/docs/astro/deploy-github-integration/) to map your Deployment to the `airflow-quickstart-complete` branch of your forked repository.
5. Select **Trigger Git Deploy** from the **More actions** menu in your Deployment settings to trigger the first deploy for the mapped repository.

	![Screenshot of the Astro UI showing how to Trigger a Git Deploy](/img/3-0_airflow-quickstart-etl_astro.png)

6. Once the deploy has completed, click the blue `Open Airflow` button on your Deployment to see the DAGs running in the cloud. From here you can jump back to [Step 4](#step-4-run-the-setup-dag) and complete the quickstart, skipping over the deploy instructions in [Step 7](#step-7-deploy-your-project), since you already deployed your project!

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