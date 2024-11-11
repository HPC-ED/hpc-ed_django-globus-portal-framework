import copy
import globus_sdk
import pandas as pd

from globus_portal_framework.gsearch import prepare_search_facets, get_index
from globus_portal_framework.gclients import load_search_client


def html_title(title):
    """
    Format the title in bold HTML tags.

    Parameters
    ----------
    title : str
        The title of the entry.

    Returns
    -------
    str
        The title wrapped in HTML <b> tags, 
        otherwise an empty string.
    """
    if title:
        return f'<b>{title}</b>'
    return ''


def html_authors(authors):
    """
    Format the author or authors into a comma separated string.

    Parameters
    ----------
    authors : list of str or str or None
        The authors of the entry. It can be a list if there are multiple
        authors. It could also be None. 

    Returns
    -------
    str
        A comma separated string of author names or author name, 
        otherwise an empty string.
    """
    if authors is None:
        return ''
    if isinstance(authors, list):
        return ', '.join(authors).replace('\\"', '"')
    else:
        return authors


def html_url(url):
    """
    Wrap the URL in an HTML anchor tag.

    Parameters
    ----------
    url : str
        The URL of the entry.

    Returns
    -------
    str
        The URL wrapped in an HTML <a> tag with attributes to open in a new tab, 
        otherwise an empty string.
    """
    if url:
        return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{url}</a>'
    return ''


def html_keywords(keywords):
    """
    Format the keywords or keyword into a comma separated string.

    Parameters
    ----------
    keywords : list of str or str or None
        The keywords of the entry. It can be a list if there are multiple
        keywords. It could also be None. 

    Returns
    -------
    str
        A comma separated string of keywords or keyword, 
        otherwise an empty string.
    """
    if keywords is None:
        return ''
    if isinstance(keywords, list):
        return ', '.join(keywords)
    else:
        return keywords


def html_abstract(abstract):
    """
    Replace escaped quotes in the abstract.

    Parameters
    ----------
    abstract : str
        The abstract of the entry.

    Returns
    -------
    str
        The abstract with escaped quotes replaced by normal quotes, 
        otherwise an empty string.
    """
    if abstract:
        return abstract.replace('\\"', '"')
    return ''


def html_duration(duration):
    """
    Check and convert the duration to a string.

    Parameters
    ----------
    duration : str or int or None
        The duration of the entry.

    Returns
    -------
    str
        The duration converted to a string,
        otherwise an empty string.
    """
    if duration:
        try:
            return str(int(duration))
        except:
            return ''
    return ''


def html_rating(rating):
    """
    Format the rating to one decimal place.

    Parameters
    ----------
    rating : str or float or None
        The rating of the entry.

    Returns
    -------
    str
        The rating formatted to one decimal place, 
        otherwise an empty string.
    """
    if rating:
        try:
            return format(float(rating), ".1f")
        except:
            return ''
    return ''


def download(search, user):
    """
    Downloads HPC-ED metadata content based on the given search criteria.

    Parameters
    ----------
    search : dict
        The dictionary `request.session['search']`, containing:
        - query : str
            The search query
        - filters : list
            The list of filters
        - index : str
            Globus index
    
    user : SimpleLazyObject
        The `request.user` object

    Returns
    -------
    status : bool
        Indicates whether downloading to HTML was successful.
    
    content : str
        The content of the HTML if successful, otherwise an error message.
    """

    # load a search client and index info
    client = load_search_client(user)
    index_data = get_index(search['index'])

    # describe the search criteria, with a limit of 1000
    search_data = {
        'q'      : search['query'],
        'facets' : prepare_search_facets(index_data.get('facets', [])),
        'filters': search['filters'],
        'limit'  : 1000
    }

    try:
        # search in the index
        result = client.post_search(index_data['uuid'], search_data)

        # columns to include in the html table, in this order
        columns = ['Title', 'Authors', 'URL', 'Keywords', 'Abstract', 'Duration', 'Rating']

        # get the relevant columns from the entries
        metadata = [
            {col: entry['entries'][0]['content'].get(col, None) for col in columns} for entry in result.data['gmeta']
        ]

        # convert to dataframe
        df = pd.DataFrame(metadata, columns=columns)
        df.index += 1

        # convert to html for a simple table with formatters
        content = df.to_html(escape=False, formatters=[
            html_title, html_authors, html_url, html_keywords, html_abstract, html_duration, html_rating
        ])

        # append a string if total searched entry is beyong 1000
        if result.data['has_next_page']:
            content = f"You have reached the output limit. 1000 out of {result.data['total']} entries downloaded." + content
        
        return True, content

    except:
        # catch any uncaught errors and output it
        return False, 'There was an error in your download, please try a different index, different query, or contact HPC-ED.'