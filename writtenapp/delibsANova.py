import csv
import operator

# f = open("rankings.txt", "w+")

with open('Decisions-Grid view.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    ranking = {}
    ratioResults = {}
    for row in readCSV:
        if row[2] == "No":
            if row[0] in ranking.keys():
                oldRatio = ranking[row[0]]
                newRatio = [oldRatio[0] + 1, oldRatio[1]]
                ranking[row[0]] = newRatio
            else:
                ranking[row[0]] = [1,0]
        elif row[2] == "Yes":
            if row[0] in ranking.keys():
                oldRatio = ranking[row[0]]
                newRatio = [oldRatio[0], oldRatio[1] + 1]
                ranking[row[0]] = newRatio
            else:
                ranking[row[0]] = [0,1]
    for k, v in ranking.items():
        yes = v[1]
        total = v[1] + v[0]
        ratio = 0
        try:
            ratio = yes / total
        except ZeroDivisionError:
            ratio = float("-inf")
        ratioResults[k] = ratio
    sorted_x = sorted(ratioResults.items(), key=operator.itemgetter(1), reverse = True)


    # print(sorted_x)

    # for k, v in ranking.items():
    #     print("Candidate: " + k + " " + "***Yes "+ ": "+ str(v[1]) + "   ***No "+ ": "+ str(v[0]))

    # print(sorted_x)

    with open('rankings.csv', "w+") as csvfile:
        wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        for x in sorted_x:
            wr.writerow(x)

    # f.write(str(sorted_x))
    # s = '\n'.join([str(x) for x in sorted_x])
    # print('\n'.join([str(x) for x in sorted_x]))
    # f.write(s)