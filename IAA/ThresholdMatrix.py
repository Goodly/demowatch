from math import exp
def evalThresholdMatrix(percentage, num_of_users, scale = 1.2, q = 1):
    """

    :param percentage: percentage agreement
    :param num_of_users: number of users
    :param scale: scales percentage, higher scale is a friendlier function, lower scale is stricter
    :param q: adjusting q adjusts the midpoint of the logistic curve, higher Qs will yield more H,
    but can make M almost never return
    :return: a code denoting the success of the inputs in this function, 'U' means too few leaders, while
    H, M, and L denote the degree  of agreement
    """
    if num_of_users<3:
        return 'U'
    percentage = percentage * scale
    kappa = num_of_users + 3
    q = 3**(-0.2 * num_of_users + 1.9) + 1
    deriv = kappa * q * exp(-kappa * (percentage - 0.5)) / (1 + q * exp(-kappa * (percentage - 0.5)))**2
    if (deriv > 1):
        return 'M'
    elif (percentage >.5):
        return 'H'
    else:
        return 'L'
def checkThreshold():
    for i in range(1,101):
        for u in range(3,11):
            p = float(i)/100
            print(str(p)+"%", u, 'users')
            print(evalThresholdMatrix(p, u))
            # print(evalThresholdMatrix(p, u, 1.4))
            # print(evalThresholdMatrix(p, u, 1.4,1.2))
            # print(evalThresholdMatrix(p, u, 1.4, 1.2))


#checkThreshold()
