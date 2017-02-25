language_name = ["C", "C++", "Pascal", "Java 1.7", "Ruby",
                 "Bash", "Python 2.7", "PHP", "Perl", "C#",
                 "Obj-C", "Free Basic", "Schema", "Clang", "Clang++",
                 "Lua", "JavaScript(ES6)", "Python 3.5", "Go", "Other Language"]

language_enable = [1, 1, 1, 1, 0,
                   1, 1, 1, 1, 1,
                   0, 0, 0, 1, 1,
                   0, 1, 1, 1, 0]

support_language = list()
for index, item in enumerate(language_enable):
    if item == 1:
        support_language.append([index, language_name[index]])

judger_name = dict([
    ('HDU','HDU'),
    ('judger_01','a'),
    ('judger_02','b'),
    ('judger_03','Almond Blossom'),
    ('judger_04','d'),
    ('judger_05','e'),
    ('vividmoon','vividmoon'),
    ('wait','waiting'),
    ('waiting','waiting'),
    ('1','H-valuate'),
    ('2','H-valuate'),
    ('H-valuated','H-valuate'),
    ('Almond Blossom','Almond Blossom'),
])

judge_result = ["Waiting",      "Waiting Rejudging",    "Compiling",    "Running",
                "Accepted",     "Presentation Error",   "Wrong Answer", "Time Limit Exceed",
                "Memory Limit Exceed", "Output Limit Exceed", "Runtime Error", "Compile Error",
                "Compile Completed"]
judge_result_color = ["Waiting",      "Waiting Rejudging",    "Compiling",    "Running",
                "#5F9EA0",     "#99CCCC",   "#990000", "#999933",
                "#999966", "#996633", "#FF6633", "#996666",
                "Compile Completed"]

judge_result_type = [
                    "active",   "active",   "active",     "active",
                    "success",  "info",  "danger",   "info",
                    "info",  "info",  "warning",   "warning",
                    ""]

code_source_style = [
        'monokai',
        'manni',
        'igor',
        'lovelace',
        'xcode',
        'vim',
        'autumn',
        'vs',
        'rrt',
        'native',
        'perldoc',
        'borland',
        'tango',
        'emacs',
        'friendly',
        'paraiso-dark',
        'colorful',
        'murphy',
        'bw',
        'pastie',
        'algol_nu',
        'paraiso-light',
        'trac',
        'default',
        'algol',
        'fruity',
    ]

index_order = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
