from ReaperEngine import ReaperEngine

class Search:
    @staticmethod
    def get_search_list(client, query):
        system_prompt = (
            "Generate a list of creative and interesting fictional search results in JSON format based on the user-provided query. "
            "Each search result should be a JSON object with the following keys: "
            "'small_logo', 'website_name', 'website_url', 'description', 'sub_links', and 'large_image'. "
            "Descriptions should creatively describe what each website offers, focusing on engaging content that would appeal to someone interested in the query topic. "
            "Sub_links should be a list of relevant topics or services offered by the website that are unique and tailored to the site's content. "
            "Ensure that each search result is unique, avoiding repetitive or overly similar entries. "
            "Websites should have inventive names and URLs that could plausibly relate to real services or topics. "
            "Here is an example of a JSON object for a single search result for a generic query 'sustainable living':\n"
            "{\n"
            "  'small_logo': 'https://ecoexample.com/eco_company_logo.png',\n"
            "  'website_name': 'Eco Example',\n"
            "  'website_url': 'https://ecoexample.com',\n"
            "  'description': 'Discover eco-friendly solutions and sustainable living ideas at Eco Example.',\n"
            "  'sub_links': ['Energy Saving Tips', 'Sustainable Home Goods', 'Eco Workshops', 'Community Initiatives'],\n"
            "  'large_image': 'https://ecoexample.com/earth_day.jpg'\n"
            "}\n"
            "\n"
            "Please generate 10 such search results in a list for the query provided. Respond ONLY with the json."
        )

        user_prompt = f"Generate search results for the query: '{query}'."

        search_page_completion = client.chat.completions.create(messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }],
            model="llama3",
            temperature=0.5,
            max_tokens=8000
        )

        return search_page_completion.choices[0].message.content

class SearchResult:
    def __init__(self, small_logo, website_name, website_url, description, sub_links, large_image):
        self.small_logo = small_logo
        self.website_name = website_name
        self.website_url = website_url
        self.description = description
        self.sub_links = sub_links 
        self.large_image = large_image
    
    def render_html(self):
        # Creating HTML for sublinks, assuming you might want to append a '#' for now as the href
        sub_links_html = ''.join(f'<a class="level-item" href="#">{text}</a>' for text in self.sub_links)

        html_content = f"""
        <div class="box">
            <article class="media">
                <figure class="media-left">
                    <p class="image is-64x64">
                        <img src="{self.small_logo}" alt="Logo">
                    </p>
                </figure>
                <div class="media-content">
                    <div class="content">
                        <p>
                            <strong>{self.website_name}</strong> <small>{self.website_url}</small>
                            <br>
                            {self.description}
                        </p>
                        <nav class="level is-mobile">
                            <div class="level-left">
                                {sub_links_html}
                            </div>
                        </nav>
                    </div>
                </div>
                <figure class="media-right">
                    <p class="image is-128x128">
                        <img src="{self.large_image}" alt="Person swimming">
                    </p>
                </figure>
            </article>
        </div>
        """
        return html_content

# Code to execute only if this module is run directly
if __name__ == "__main__":
    engine = ReaperEngine()
    search_results = Search.get_search_list(engine.client, "adventure sports travel")
    print(search_results)