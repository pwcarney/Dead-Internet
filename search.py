from ReaperEngine import ReaperEngine
import json
from bs4 import BeautifulSoup

class Search:
    @staticmethod
    def get_search_list(client, query):
        system_prompt = (
            "Generate a list of creative and interesting fictional search results in JSON format based on the user-provided query. "
            "Each search result should be a JSON object with the following keys: "
            "'small_logo', 'website_name', 'website_url', 'description', 'sub_links', and 'large_image'. "
            "Descriptions should creatively describe what each website offers, focusing on engaging content that would appeal to someone interested in the query topic. Vary the tone of the descriptions. Some sites might use formal language as a B2B service, others might be warm and engaging, aiming at families or individuals."
            "Sub_links should be a list of relevant topics or services offered by the website that are unique and tailored to the site's content. "
            "Each search result should reflect a different facet of the query topic. For instance, if the query is 'sustainable living', some results could focus on sustainable fashion, while others might specialize in green technology or organic farming. "
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
    
    @staticmethod
    def parse_search_results(search_results):
        # Parse the JSON search results into a list of SearchResult objects
        search_results_list = []
        for result in search_results:
            print(result)
            search_result = SearchResult(
                small_logo=result['small_logo'],
                website_name=result['website_name'],
                website_url=result['website_url'],
                description=result['description'],
                sub_links=result['sub_links'],
                large_image=result['large_image']
            )
            search_results_list.append(search_result)
        
        return search_results_list

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
    

if __name__ == "__main__":
    engine = ReaperEngine()
    user_query = "adventure sports travel"
    search_results = Search.get_search_list(engine.client, user_query)
    search_results_object_list = Search.parse_search_results(json.loads(search_results))
    html_content = '\n'.join([result.render_html() for result in search_results_object_list])

    # Load the HTML file
    with open('static/html/base_templates/search.html', 'r') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Find the search input box and update its value with the user query
    search_input = soup.find('input', {'class': 'input'})
    if search_input:
        search_input['value'] = user_query

    # Find the placeholder or a specific container where results should be inserted
    results_container = soup.find(id='results-container')
    if not results_container:
        results_container = soup.new_tag('div', id='results-container')
        soup.body.append(results_container)

    # Clear existing content if needed and insert new HTML
    results_container.clear()
    new_content = BeautifulSoup(html_content, 'html.parser')
    results_container.append(new_content)

    # Write the updated HTML back to the file
    with open('static/html/search.html', 'w') as file:
        file.write(str(soup))