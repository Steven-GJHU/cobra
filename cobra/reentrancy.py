
warning = []

# node: file node
def check_reentrancy(node):
    # pp.pprint(file)
    for contract in node["body"]:
        # find(node)
        # check_low_level_func_return(contract)
        state_var = find_state_var(contract)
        # print(state_var)
        for statement in contract["body"]:
            if statement["type"] == "FunctionDeclaration":
                check_func_reentrancy(statement, state_var)
                # check_func_reentry(statement, state_var)
    #     print(len(warning))
    return warning


# node: contract node
def find_state_var(node):
    state_var = []
    for statement in node["body"]:
        if statement["type"] == "StateVariableDeclaration":
            state_var.append(statement["name"])
    return state_var


# DFS find all if-statement and return vars in conditions
# def find_if_var(node, if_var):
#     if node["type"] == "IfStatement":
#         if node["test"]["type"] == "BinaryExpression":
#             for side in ["left", "right"]:
#                 if node["test"][side]["type"] == "Identifier":
#                     if node["test"][side]["name"] not in if_var:
#                         if_var[node["test"][side]["name"]] = node["start"]
#                 elif node["test"][side]["type"] == "MemberExpression":
#                     if node["test"][side]["object"]["name"] not in if_var:
#                         if_var[node["test"][side]["object"]["name"]] = node["start"]
#         elif node["test"]["type"] == "UnaryExpression":
#             pass
#         if "body" in node["consequent"]:
#             for statement in node["consequent"]["body"]:
#                 find_if_var(statement, if_var)
#     else:
#         pass

# Remain for test 20181007 start
# find if statements of interaction part
def find_if_var(node, interact_var, state_var):
    if node["test"]["type"] == "BinaryExpression":
        """
        To Be continue...
        This is the check part of checks-effects-interactions
        """
        pass
    elif node["test"]["type"] == "UnaryExpression" and node["test"]["operator"] == "!":
        if "argument" in node["test"]:
            find_require_stmt(node["test"]["argument"], interact_var)
    elif node["test"]["type"] == "CallExpression":
        find_require_stmt(node["test"], interact_var)
    if "body" in node["consequent"]:
        for statement in node["consequent"]["body"]:
            if statement["type"] == "IfStatement":
                find_if_var(statement, interact_var, state_var)
            elif statement["type"] == "ExpressionStatement":
                find_require_var(statement, interact_var)
            if len(interact_var) > 0:
                check_effects(statement, interact_var, state_var)

# find require statements of interaction part
def find_require_var(node, interact_var):
    if "callee" in node["expression"] and "name" in node["expression"]["callee"]:
        if node["expression"]["type"] == "CallExpression" and node["expression"]["callee"]["name"] == "require":
            # print (node["expression"]["type"] + node["expression"]["callee"]["name"])
            if "arguments" in node["expression"]:
                for args in node["expression"]["arguments"]:
                    find_require_stmt(args, interact_var)


def find_require_stmt(stmt, interact_var):
    if stmt["type"] == "CallExpression" and stmt["callee"]["type"] == "CallExpression":
        find_require_stmt(stmt["callee"], interact_var)
    elif stmt["type"] == "CallExpression" and stmt["callee"]["type"] == "MemberExpression":
        if stmt["callee"]["property"]["name"] == "value" and stmt["callee"]["object"]["property"]["name"] == "call":
            for arg in stmt["arguments"]:
                interact_arg = get_interact_args(arg)
                # print("!!!!!!!!!interact_var: " + interact_arg)
                interact_var.append(interact_arg)
        else:
            pass
    else:
        pass

def get_interact_args(node):
    if node["type"] == "Identifier":
        return node["name"]
    elif node["type"] == "Literal":
        return str(node["value"])
    elif node["type"] == "BinaryExpression" and "operator" in node:
        left = get_interact_args(node["left"])
        right = get_interact_args(node["right"])
        return str(left + node["operator"] + right)
    elif node["type"] == "MemberExpression":
        object = str(get_interact_args(node["object"]))
        property = str(get_interact_args(node["property"]))
        if object == "msg":
            return str(object + "." + property)
        else:
            return str(object + "[" + property + "]")
    else:
        return None

# Remain for test 20181007 end

# def find_call(node, state_var, if_var, flag):
#     try:
#         if "start" in node:
#             if not flag[0] and "type" in node and node["type"] == "CallExpression":
#                 flag[0] = True
#             if flag[0]:
#                 if "expression" in node and node["expression"]["type"] == "AssignmentExpression":
#                     if "object" in node["expression"]["left"]:
#                         name = node["expression"]["left"]["object"]["name"]
#                     else:
#                         name = node["expression"]["left"]["name"]
#                     if name in state_var and name in if_var:
#                         warning.append(Warning(if_var[name], node["end"],
#                                                "Could potentially lead to re-entrancy vulnerability\n"
#                                                "http://solidity.readthedocs.io/en/develop/security-considerations.html#re-entrancy"))
#                         # print("Find re-entry at [", if_var[name], node["end"], "]")
#         # Iterate through current node's children
#         for _, value in node.items():
#             if isinstance(value, list):
#                 for obj in value:
#                     find_call(obj, state_var, if_var, flag)
#             else:
#                 find_call(value, state_var, if_var, flag)
#         pass
#     except:
#         pass


# node: function node
# def check_func_reentry(node, state_var):
#     # array of all statements in the function
#     if_var = {}
#     for obj in node["body"]["body"]:
#         # find all if-statement: return set of vars
#         find_if_var(obj, if_var)
#     # find first call statement
#     if len(if_var) == 0:
#         return
#     flag = [False]
#     find_call(node, state_var, if_var, flag)
#     # check statement after that, change set of vars or not

def check_func_reentrancy(node, state_var):
    interactions = []
    for obj in node["body"]["body"]:
        checks_effects_interactions(obj, interactions, state_var)


def checks_effects_interactions(node, interacts, state_var):
    if node["type"] == "IfStatement":
        find_if_var(node, interacts, state_var)
    elif node["type"] == "ExpressionStatement":
        find_require_var(node, interacts)
        if len(interacts) > 0:
            check_effects(node, interacts, state_var)

def check_effects(node, interacts, state_var):
    if node["type"] == "ExpressionStatement" and node["expression"]["type"] == "AssignmentExpression":
        if "object" in node["expression"]["left"]:
            left_effect_var = node["expression"]["left"]["object"]["name"]
        else:
            left_effect_var = node["expression"]["left"]["name"]
        right_effect_var = get_interact_args(node["expression"]["right"])
        # print("??????left_effect_var: " + str(left_effect_var))
        # print("++++++right_effect_var:" + str(right_effect_var))
        if left_effect_var in state_var:
            for i in interacts:
                if i in right_effect_var:
                    warning.append(i)
    elif node["type"] == "IfStatement" and "body" in node["consequent"]:
        for statement in node["consequent"]["body"]:
            check_effects(statement, interacts, state_var)
    else:
        pass



# def check_low_level_func_return(node):
#     if isinstance(node, list):
#         for f in node:
#             check_low_level_func_return(f)
#         return
#     elif isinstance(node, dict):
#         if node["type"] == "IfStatement":
#             return
#         if node["type"] == "Identifier" and "name" in node and node["name"] == "call":
#             warning.append(Warning(node["start"], node["end"], "Low-level call() result unchecked\n"
#                                                                "https://github.com/ConsenSys/smart-contract-best-practices#external-calls"))
#             # print("Find not check call() return value at [", node["start"], node["end"], "]")
#         else:
#             for f in node:
#                 check_low_level_func_return(node[f])


# Check static error
# def find(node):
#     try:
#         if "start" in node:
#             start = node["start"]
#             end = node["end"]
#             if "name" in node:
#                 name = node["name"]
#                 if name == "sha3":
#                     warning.append(Warning(start, end, "Use keccak256() instead of sha3()\n"
#                                                        "https://github.com/ethereum/EIPs/issues/59"))
#                     # print("Find sha3() at [", start, end, "], please change to keccak256()")
#                 elif name == "send":
#                     warning.append(Warning(start, end, "Use transfer() instead of send()\n"
#                                                        "http://solidity.readthedocs.io/en/develop/types.html#members-of-addresses"))
#                     # print("Find send() at [", start, end, "], please change to transfer()")
#                 elif name == "suicide":
#                     warning.append(Warning(start, end, "Use selfdestruct() instead of suicide()\n"
#                                                        "https://github.com/ethereum/EIPs/blob/master/EIPS/eip-6.md"))
#                     # print("Find suicide() at [", start, end, "], please change to selfdestruct()")
#             if "type" in node and node["type"] == "ThrowStatement":
#                 warning.append(Warning(start, end, "Use revert() instead of throw\n"
#                                                    "https://solidity.readthedocs.io/en/develop/control-structures.html#error-handling-assert-require-revert-and-exceptions"))
#                 # print("Find throw at [", start, end, "], please change to revert()")
#         # Iterate through current node's children
#         for _, value in node.items():
#             if isinstance(value, list):
#                 for obj in value:
#                     find(obj)
#             else:
#                 find(value)
#     except:
#         pass
