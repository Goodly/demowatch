
Steps to run Inter-Annotator Agreement on exported Highlighter CSV files.

1. virtualenv --python=python3 ../iaa.env
1. source ../iaa.env/bin/activate
1. pip install -r requirements.txt
1. cd SemanticsTriager1.4C2/
1. python3 TriagerScoring.py -i ProjectName-2019-04-04T1905-Highlighter.csv


Output file is in current directory, prefixed with T_IAA

For MacOS using `conda` (last updated 2019-04-08):

One time setup:

1. Create `conda` environment: `conda create --name iaa`
1. Activate `conda` environment: `conda activate iaa`
1. Install necessary libraries:
	- `conda install pandas`
	- `pip install krippendorff`
1. Deactivate `conda` environment: `deactivate iaa`

Each time IAA needs to be run.

1. Look up the Project that needs IAA.
1. Go to the Project menu (2nd column of links on TagWorks dashboard) and "Retrieve Task Runs" and then "Export Task Runs".
1. The Export Task Runs menu will take you to /researcher/datafiles/. The most recent export is on the top. You may need to refresh until "Processing" changes to "Ready".
1. Download the data file (filename will be like `ProjectName-2019-04-04T1905-Highlighter.csv.gz`)
	- On Mac there is a bug where the `.gz` is stripped off without actually decompressing. So add the `.gz` back and then decompress.
1. `cd` to where the decompressed `csv` file resides.
1. Activate `conda` environment: `conda activate iaa`
1. Run `python3 TriagerScoring.py ProjectName-2019-04-04T1905-Highlighter.csv`
1. Go back to the Project screen that you chose "Export Task Runs" from. Click on the link "Imported IAA tags will be saved to: ProjectName.IAA". Click "Upload TUAs" and select the output file (prefixed with T_IAA) and upload it. If it contains TUAs that have not been previously loaded, the summary counts should increase after waiting a few seconds and refreshing the page.
1. Deactivate `conda` environment: `deactivate iaa`
