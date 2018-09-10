import csv
import operator

# f = open("rankings.txt", "w+")

scores_file_name = "anova_fall18_interview_ratings.csv"
all_applicants_file_name = "anova_fall18_all_applicants.csv"
out_file_name = "out.csv"

def getApplicantInfo(csv_file_name, columns):
    """
    Given a list of column names, return a map
    Applicant Name --> [col1, col2, ...]
    """
    assert columns, "No Columns to read"
    out = {}
    col_indices = []
    with open(csv_file_name) as csvfile:
        row_iter = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(row_iter):
            if i == 0:
                # init list of column indices we want to read
                col_indices = [j for j in range(len(row)) if row[j] in columns]
                # print(col_indices)
                # exit(0)
            else:
                out[row[0]] = [row[j] for j in col_indices]
    return out

def getScores(csv_file_name):
    """
    Gets the avg score of candidate
    Return sorted list of (Canidate_Name, Score) in DSC order
    """
    with open(csv_file_name) as csvfile:
        # Iterator over rows in a table
        row_iter = csv.reader(csvfile, delimiter=',')
        # Applicant --> Score
        applicant_to_score = {}
        # Applicant --> # of reviwers 
        applicant_to_entries = {}
        """
        TABLE
        Name | Interviewer | Rating | Notes
        """
        # Iterate through rows to get scores
        for i, row in enumerate(row_iter):
            if i == 0:
                # First Row is col names, skip it
                continue
            # Validate values in row
            for j, data in enumerate(row):
                if j == 3:
                    # Notes col can be empty
                    continue
                assert row, "Row {} contains empty field".format(i)

            candidate_name = row[0].strip()
            interviewer_name = row[1]
            rating = int(row[2])
            notes = row[3]

            if candidate_name not in applicant_to_score:
                applicant_to_score[candidate_name] = rating
                applicant_to_entries[candidate_name] = 1
            else:
                applicant_to_score[candidate_name] += rating
                applicant_to_entries[candidate_name] += 1

    # Make sure all applicants have 3 reviewers
    # Find avg score of each applicant
    for applicant, entries in applicant_to_entries.items():
        assert entries == 3, "{} does not have 3 reviewers. Has {}".format(applicant, entries)
        applicant_to_score[applicant] /= 3

    # List of tuples (k,v) with k,v of applicant_to_scores sorted DSC by v
    return sorted(applicant_to_score.items(), key=operator.itemgetter(1), reverse=True)

if __name__ == "__main__":

    # [(name, score), ...] sorted DSC by score
    scores = getScores(scores_file_name)
    # name --> [info...]
    committee_prefs = getApplicantInfo(all_applicants_file_name, ["Which committee is your first choice?", "Which committee is your second choice?"])
    # print(committee_prefs)
    # print("Peter Aydin Sorenson" in committee_prefs)
    out = [[row[0], row[1]] + committee_prefs[row[0]] for row in scores]

    # Write to out file
    with open(out_file_name, "w+") as csvfile:
        wr = csv.writer(csvfile)
        wr.writerows(out)
