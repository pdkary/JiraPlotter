# JiraPlotter
A data visualization project for analyzing sprint velocity

**This project is WIP**

## Usage
After inputting your Jira-Api token, username, and server domain into the **resources.py** file, in the main method of **jiraplotter.py** create a new instance of **JiraPlotter** 
```
projectKey = "Integrations"
jiraplotter = JiraPlotter(projectKey)
jiraplotter.get_figure()
```
The graph for the project "Integrations" will now appear as **static/images/Integrations_\<date\>.png***

