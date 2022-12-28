import openai

event_prefix = "<event "
event_suffix = "</event>"

# Events types
SPEECH = "speech"
ACTION = "action"
ENV_EVENT = "environment"

class OpenAI:

    def __init__(self, name, chat_name):
        # Obtem a chave de acesso da OpenAI do arquivo key.json
        openai.api_key = open("keys/openai.txt").read()

        self.history = ""
        self.rules = []
        self.name = name
        self.chat_name = chat_name

    def rules_str(self):
        # retorna uma string com as regras numeradas e separadas por quebra de linha
        # O índice da regra começa em 1
        return "\n".join([f"[{i+1}] {m}" for i, m in enumerate(self.rules)])

    def call_openai(self, prompt):
        # Cria um modelo de completação usando o GPT-3 da OpenAI
        completion_model = openai.Completion.create(
            engine="text-davinci-003",
            prompt= prompt,
            temperature=0.7,
            max_tokens=256,
            stop=[event_prefix, event_suffix]
        )

        # Obtem a sugestão de completamento do texto
        completed_text = completion_model["choices"][0]["text"]

        if completed_text == "":
            completed_text = "..."

        return completed_text

    def get_response(self):
        self.history += f'{event_prefix}type="{SPEECH}" username="{self.name}">'

        # Chama a OpenAI para completar o texto
        completed_text = self.call_openai(self.rules_str() + "\n\n" + self.history)

        self.history += completed_text + event_suffix + "\n"

        # Printa as regras e o histórico	
        print(f"{self.rules_str()}\n\n{self.history}")

        return completed_text

    def new_event(self, event_type, prompt, user=None, complete=True):

        user_attr = ""
        if user is not None:
            user_attr = f' username="{user}"'

        prompt = f'{event_prefix}type="{event_type}"{user_attr}>{prompt}{event_suffix}\n'
        self.history += prompt
        
        if not complete:
            # Printa as regras e o histórico	
            print(f"{self.rules_str()}\n\n{self.history}")
            return ''

        return self.get_response()

    def act_as_user(self, user, prompt, complete=True):
        return self.new_event(ACTION, prompt, user, complete)
    
    def say_as_user(self, user, prompt, complete=True):
        return self.new_event(SPEECH, prompt, user, complete)

    def env_happen(self, prompt, complete=True):
        return self.new_event(ENV_EVENT, prompt, complete=complete)

    def poke(self):
        return self.get_response()

    def add_rule(self, prompt):
        rules = prompt.split("\n")
        self.rules += rules

    def remove_rule(self, index):
        index -= 1
        self.rules.pop(index)
    
    def clear_rules(self):
        self.rules = []
    
    def clear_history(self):
        self.history = ""
