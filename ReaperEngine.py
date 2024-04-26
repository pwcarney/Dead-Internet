from openai import OpenAI
from bs4 import BeautifulSoup
from ImageGen import ImageGen

''' About the name...
I apologise for it sounding pretentious or whatever, but I dont care it sounds cool and cyberpunk-y(-ish)
and fits with the Dead Internet Theory theme of this little project
'''

class ReaperEngine:
    def __init__(self):
        self.client = OpenAI(base_url="http://localhost:11434/v1/") # Ollama is pretty cool
        self.internet_db = dict() 

        self.image_gen = ImageGen() 

        self.temperature = 2.1
        self.max_tokens = 8000

    def _format_page(self, dirty_html):
        soup = BeautifulSoup(dirty_html, "html.parser")

        # Check if <head> exists, if not create one
        head = soup.head
        if head is None:
            head = soup.new_tag("head")
            soup.html.insert(0, head)

        # Add the stylesheet link
        link_tag = soup.new_tag("link", rel="stylesheet", href="static/ghost.css")
        head.append(link_tag)

        # Image generation
        for img in soup.find_all("img"):
            src = img.get("src", "")
            if src.startswith("generate:"):
                prompt = src.split("generate:", 1)[1]
                output_name = "gen_" + prompt.replace(" ", "_")[:50] 
                self.image_gen.generate_image(prompt, output_name)
                img['src'] = f"./images/{output_name}.png"

        # Process anchor tags as before
        for a in soup.find_all("a"):
            if "mailto:" in a["href"]:
                continue
            a["href"] = a["href"].replace("http://", "").replace("https://", "")
            a["href"] = "/" + a["href"]

        # Additional HTML modifications as before
        home_button = soup.new_tag("a", href="/")
        home_button.string = "Home"
        body = soup.body
        if body:
            body.insert(0, home_button)

        return str(soup)
    
    def get_index(self):
        # Load the HTML content from index.html
        with open("index.html", "r") as file:
            return file.read()

    def get_page(self, url, path, query=None):
        # Return already generated page if already generated page
        try: return self.internet_db[url][path]
        except: pass
        
        # Construct the basic prompt
        prompt = f"Give me a webpage from the fictional site of '{url}' at the resource path of '{path}'. Make sure all links generated either link to an external website, or if they link to another resource on the current website have the current url prepended ({url}) to them. For example if a link on the page has the href of 'help' or '/help', it should be replaced with '{url}/help'."
        # TODO: I wanna add all other pages to the prompt so the next pages generated resemble them, but since Llama 3 is only 8k context I hesitate to do so

        # Add other pages to the prompt if they exist
        if url in self.internet_db and len(self.internet_db[url]) > 1:
            pass
        
        # Generate the page
        generated_page_completion = self.client.chat.completions.create(messages=[
            {
                "role": "system",
                "content": self.system_prompt
            },
            {
                "role": "user",
                "content": prompt
            }],
            model="llama3", # What a great model, works near perfectly with this, shame its only got 8k context (does Ollama even set it to that by default?)
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

        # Add the page to the database
        generated_page = generated_page_completion.choices[0].message.content
        if not url in self.internet_db:
            self.internet_db[url] = dict()
        self.internet_db[url][path] = self._format_page(generated_page)

        open("curpage.html", "w+").write(generated_page)
        return self._format_page(generated_page)
    


