from typing import List
import yaml


class ReadFromYAMLName():

    def __init__(self, title, description) -> None:
        self.title = title
        self.description = description

    def __repr__(self) -> str:
        # return "%s(name=%r)" % (
        #     self.__class__.__name__, self.name
        # )

        return f"{self.title}\n{self.description}\n"

class ReadFromYAMLAnswer():
    def __init__(self, shell, result) -> None:
        self.shell = shell
        self.result = result

    def __repr__(self) -> str:
        # return "%s(shell=%r, result=%r)" % (
        #     self.__class__.__name__, self.shell, self.result
        # )

        return f"{self.shell}\n{self.result}\n"


class ReadFromYAMLHint():
    def __init__(self, hint1, hint2) -> None:
        self.hint1 = hint1
        self.hint2 = hint2

    def __repr__(self) -> str:
        # return "%s(hint1=%r, hint2=%r)" % (
        #     self.__class__.__name__, self.hint1, self.hint2
        # )

        return f"{self.hint1}\n{self.hint2}\n"


def get_data_from_yaml(filename: str) -> tuple:

    with open(filename) as file:
        yaml_load_obj: list = yaml.safe_load(file)

    # print(yaml_load_obj[1])

    conf_name_list: List[ReadFromYAMLName] = []
    conf_answer_list: List[ReadFromYAMLAnswer] = []
    conf_hint_list: List[ReadFromYAMLHint] = []

    for obj in yaml_load_obj:
        conf_name: ReadFromYAMLName = ReadFromYAMLName(obj['title'], obj['description'])
        conf_name_list.append(conf_name)
        conf_answer: ReadFromYAMLAnswer = ReadFromYAMLAnswer(obj['answer']['shell'], obj['answer']['result'])
        conf_answer_list.append(conf_answer)
        conf_hint: ReadFromYAMLHint = ReadFromYAMLHint(obj['hint']['hint1'], obj['hint']['hint2'])
        conf_hint_list.append(conf_hint)

    # print(f"{conf_name_list}\n{conf_answer_list}\n{conf_hint_list}")
    return conf_name_list, conf_answer_list, conf_hint_list
