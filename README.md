# DemoWatch

Authors: Sidney Le, Lucy Portnoff, Schuyler Ross, Aaron Ngai, Isanette Carreon

### THE IDEA 

Sociological theory concerning protest movements, and the events they manifest in, is missing something. In particular, it is missing a significant empirical foundation — a way to perform natural experiments or retroactive studies to determine **how exactly these events unfold**. What actions in what sequence cause, say, violence to occur at a rally or a march? Without empirical analysis, causal linkages between actions and their consequences are difficult to establish.

### PROJECT OVERVIEW

DemoWatch is a way to generate the data and enable the empirical analysis, using the **Occupy Movement** as a natural experiment and data source. News articles are the proxy by which data can be gleaned from these events, which are by nature difficult to quantify. 

**TagWorks**, formerly known as TextThresher, is a platform for easily crowdsourcing the tasks of annotating and parsing text data, developed with DemoWatch and adjacent projects in mind. The backend involves an algorithm of **inter-annotator agreement (IAA)** to ensure high-quality “consensus” information is generated. 

TagWorks works primarily by having annotators answer questions and sometimes highlight text to justify their answers. A specific, contained set of questions and answers is called a **schema**. A significant amount of sociological theory is fit into a few dozen questions and their respective answers. The questions are presented in a hierarchical fashion, where specific answers to a question may prompt follow-up questions. There is a whole section of the DemoWatch project that is just schema development. This involves having a dedicated team of well-trained volunteers user-test the schema, file bug reports, and work on iterating the schema.

How can you tell if the event being described in one news article is the same event being described in another news article? Some things may pop out: place, date, number of people, etc. Humans are particularly good at answering this question because our brains can naturally understand the higher-order meanings in the text. For a text parser, the task is much harder. 

This is especially relevant for us because we’re interested in understanding events, but all we have are news texts. The texts do not have a convenient tag attached to them denoting a unique event ID, which we need to access. 

We can approximate the unique events through a process called **canonicalization**. This is the work that Sidney, Jacob, Aaron, Schuyler, Avik, and Devesh developed. See the subsection below for more details.

Finally, after our canonicalization algorithm has generated a canonical set of events (with associated actions, features, and timesteps), we can perform a quantitative analysis of police-protester interactions. This portion of the project is continually being expanded. Thus far, we have focused primarily on modelling interactions within and among events using regression analysis and dynamic Bayesian networks (probabilistic models). 

To clarify the motivation for our project and its major subparts, we have also authored the more detailed documentation below.

### OCCUPY MOVEMENT

The DemoWatch project is based on the Occupy Movement, a nationwide protest on economic inequality spanning from 2011-2012. At the time, protests were occurring in nearly every major American city, with heavy media coverage following close by. Through this fortunate combination of events, we found an abundant data source, with a wide sample size and precise investigative scope. It is only because of this that our research could exist at all.

Generally, people protested against Wall Street through three activities. First, they would attempt to picket the political center of their respective cities (i.e. the city hall and surrounding areas). These events usually lasted for weeks, months, or years, with police intermittently breaking up the protest grounds. Sometimes even encampments would result, and protesters would actively prevent city council members from making legislative decisions. The next place that people targeted were the banks. Again, protesters would blockade their local commercial banking branch, stopping customers and bankers from commencing business. At times, mass confrontations would result, such that police riot squads would shoot tear gas and arrest belligerent individuals, effectively dissolving the crowd. Of course, collateral damage from these fights created bad press, and tougher government restrictions were imposed. Finally, if no other locations were available, protesters would march throughout the city. Whether these marches followed city regulations would vary, but no conflicts happened unless violent behavior erupted.

The story is incomplete without the administration’s point of view. In coordination, the police department and municipal government tried to negotiate with the protesters, often issuing public statements. Sometimes, they would ask for testimony from other individuals, like knowledge specialists and the protesters themselves.

All this data was collected by web-scraping the Internet, searching for relevant newspapers and web articles. To learn more, please refer to Chapters 1 and 2 of: https://gke.mybinder.org/v2/gh/Goodly/CapitolQuery_SSRC/master.

### SCHEMA

Schemas are the primary way that Demo Watch collects text data from news articles. Rather than relying on natural language processing, which often misses or misconstrues text data, Demo Watch asks users to answer questions about the information they are reading. The sets of questions are called schemas, and allow us to extract information in relation to specific themes. Each schema has its own theme (such as police activities, protester activities, camps, etc). For each schema, we set up a “project” on Tagworks where users can answer the schema’s questions for many news articles. Users complete the schema fully before moving on to the next article.

Importantly, users will rarely be prompted to answer every single question in the schema. Each successive question depends on the answer that was just given. For example, if a person answers that no arrests were made but that there was an injury, the schema will bypass all questions related to arrests and direct the user to questions about injuries. 

Directions from answers to the next questions are identified using numerical codes in the schemas. Each question is labeled with a number, and each answer is labeled with the number of the next question. This format must be followed when drafting the schemas so that TagWorks can recognize the directions. We typically draft the schemas in Overleaf first and then upload them to TagWorks.   

The questions themselves are based on sociological theories of police-protester interactions.

### TAGWORKS

Tagworks can be seen as the link between schema development and inter-annotator agreement. Here, volunteer collaborators recount the experiences of the Occupy Movement news stories, refocused within the lens of our research agenda. This raw data will then be verified by later supervising algorithms and annotators.

This is accomplished through a Pybossa framework developed by a company associated with Goodly Labs. Currently, our team’s role is to contribute annotation volunteer hours, and to submit bug reports whenever schema or user interface issues arise.

To access an example TagWorks page, begin a project oh the following site: https://df.goodlylabs.org/.

The left hand side of the web page represents pre-selected portions of the news articles that a preliminary algorithm has deemed interesting enough for annotators to read. Annotators can highlight portions of the text to supplement their schema selections, adding context for further analysis. Recent discussion has brought the possibility for event-based highlighting, where annotators can specify events to associated with certain texts. If implemented, this feature would require editing a spinbox to indicate the event number.

Conversely, the right hand side shows a series of schema questions that dynamically elaborate themselves. Whenever the user answers a question, TagWorks references the schema to see if more details are required for that answer. If so, more of the numbered tabs will appear, allowing straightforward translation from schema to questions.

Overall, users can contribute to a growing body of research about police-protester interactions, simply by interpreting relevant news articles for computational parsing and modeling. If especially proactive, one can even appear on the Goodly Labs leaderboard!

### INTER-ANNOTATOR AGREEMENT (IAA) 

Let’s begin by considering the motivation for creating an inter-annotator agreement (IAA) algorithm. As described above, each annotation task is assigned to multiple crowdworkers on the internet. For the sake of simplicity, let’s say that ten individuals complete each task. The output of TagWorks, then, is a set of ten responses per task. This is not particularly useful. We do not want ten (potentially conflicting) datasets for every uploaded TUA; instead, we want each TUA to be associated with a single, canonical set of data. Hence the IAA algorithm: our computational machinery for condensing multiple users’ responses into a single, canonical data collection.

Formally, we can evaluate IAA in classic algorithmic terms--by considering its inputs, outputs, and behavior.
- *Input*: The three CSV files produced by TagWorks (schema, highlighter, and question-answer), in which every individual user’s responses are stored in separate rows.
- *Output*: A single CSV file in which rows correspond to single questions in particular task runs, with all users’ disparate responses condensed into a single answer set.
- *Behavior*: Use Krippendorf’s Alpha and other mathematical processes to determine levels of agreement between multiple users’ answers, evaluate whether they can be reduced to a single answer (set) per question, perform the reduction if possible, and ensure that agreement holds along chains of logically dependent questions.

Running the IAA code requires a bit of setup work on the part of the user. Follow the steps detailed below. (NOTE: the following information is accurate as of September 18th, 2019. It may need to be updated as future iterations of IAA code are released).
1. **Download the input files.** First you will need to download copies of the TagWorks output files for your project--specifically, the question-answer, highlight, and schema CSVs. These will serve as the input files for the IAA code. Some of your colleagues should have TagWorks admin access to retrieve the files, if you do not personally. Two important notes: (1) make sure the files are unzipped before proceeding, and (2) do not change the names of the files, even slightly.
2. **Clone the GitHub repo.** Using the standard git clone procedure, clone the DemoWatch GitHub repo onto your local machine (or, if it already exists locally, git pull to make sure your copy is accurate). 
3. **Create the relevant directories.** Navigate to the IAA folder in the DemoWatch repo. Once inside, you’ll need to create three new sub-folders: one in the ‘data’ folder, one in the ‘output’ folder, and one in the ‘scoring’ folder. Please give all three new folders the same name. While the particular content of the name does not matter, it would be useful to include the date that you’re running the IAA code (e.g., “setup_testing_4-26-19”).
4. **Edit the code.** Now, using your favorite text editor, open the Master.py file (in the IAA directory). Scroll to line 46, where the ‘input_dir’, ‘output_dir’, and ‘scoring_dir’ variables are defined. Reassign them to the names of the sub-folders you just created (keeping the same ‘./’ pathing format that already exists). Make sure to save your changes.
5. **Execute the code.** Open a command prompt window, navigate to the IAA directory, and execute the Master.py python file. This will run the IAA algorithm on the TagWorks CSVs, generating two new output CSVs (described below). It will likely take ~10 minutes to finish. You don’t need to pass any arguments to Master.py. You will need to use python 3.7, so set up an environment with Anaconda if necessary. (Note: the code may error because certain packages are not installed; if this occurs, just use pip to install the packages locally.)
6. **Retrieve the output files.** IAA will generate two output CSV files. One will be located in the IAA/output/ sub-folder that you created in step (3). This is the raw output file. The other output CSV will be located in the IAA/scoring/ sub-folder you created in step (3). This file is a filtered version of the raw output data. First, all rows for questions with insufficient agreement have been deleted. Second, the algorithm has checked for logical dependency chains among questions, and for all questions with insufficient agreement, it has deleted all rows for logically-dependent child questions.

### CANONICALIZATION

The canonicalization algorithm consists of four major subparts, outlined below:
1. **Data Wrangling:** This involves reformatting the data structure of the IAA output to be something that is usable for data science purposes.
2. **Event Label Generation:** Individual texts, if they are about the same event, should have the same event label. Note that at this time, we are using a naive date-place labeling scheme, where unique combinations of event date (note, *not* publishing date) and place are enough to signify an initial partition of events.
3. **Clustering:** With the assumption that partitioning by date and place will tend towards under-identifying unique events, we run the event groups, each of which consists of all of the texts identified as the event and the answer features related to those texts, through an agglomerative clustering algorithm, which takes into account information about the specific question features. The final clusters are now the final unique event groups. 
4. **Compacting:** This simply takes each unique event group and collapses the rows of features into a single row of features by taking the max (in the case of categorical features) or the mean (in the case of quantitative features). At this stage, we now have a single row of features describing each event. 

Notice that the events themselves are what we are trying to approximate with this process, and not the features related to those events.
