#!/usr/bin/env python
"""
    A category mapping module
"""

categories = {
    "Politics": [
        "Politics",
        "Courts & Law",
        "Courts And Law",
        "Fact Checker",
        "The Fix",
        "Monkey Cage",
        "Polling",
        "Congress",
        "White House",
        "Right Turn",
        "GovBeat",
        "In the Loop",
        "DemocracyPost",
        "The Volokh Conspiracy",
        "Federal Insider",
        "2chambers",
        "The Fed Page",
        "Community Relations",
        "World Politics",
        "Wonkblog",
        "Post Politics",
        "Think Tanked",
        "PowerPost",
        "Jennifer Rubin",
    ],
    "Opinions": [
        "Opinions",
        "Opinion",
        "The Post's View",
        "Act Four",
        "Global Opinions",
        "Local Opinions",
        "Letters to the Editor",
        "The Opinions Essay",
        "The Plum Line",
        "Post Opinión",
        "Post Opinion",
        "Alexandra Petri",
        "Telnaes Cartoons",
        "Toles Cartoons",
        "Erik Wemple",
        "In Theory",
        "The Watch",
        "Post Partisan",
        "PostPartisan",
        "Post Local",
        "Blogs & Columns",
    ],
    "Investigations": [
        "Investigations",
        "Investigative",
    ],
    "Tech": [
        "Tech",
        "Consumer Tech",
        "Future of Transportation",
        "Innovations",
        "Internet Culture",
        "Space",
        "Tech Policy",
        "Video Gaming",
        "The Intersect",
        "The Switch",
        "On I.T.",
        "Technology",
    ],
    "World": [
        "World",
        "Africa",
        "Americas",
        "Asia",
        "Europe",
        "Middle East",
        "Drawing The World Together",
        "The Americas",
        "WorldViews",
        "Asia & Pacific",
    ],
    "D.C., Md. & Va.": [  # Local news
        "Maryland Politics",
        "D.C., Md. & Va",
        "The District",
        "Maryland",
        "Virginia",
        "Crime & Public Safety",
        "Public Safety",
        "Education",
        "Going Out Guide",
        "Restaurants & Bars",
        "Transportations",
        "Cars",
        "All Opinions Are Local",
        "D.C.",
        "Virginia Politics",
        "D.C. Politics",
        "Bars & Clubs",
        "Md. Politics",
        "Restaurants",
        "On Faith Local",
        "Maryland Terrapins",
        "District of DeBonis",
        "A House Divided",
        "Local",
        "Digger",

    ],
    "Sports": [
        "Sports",
        "NFL",
        "MLB",
        "NBA",
        "NHL",
        "Boxing & MMA",
        "College Sports",
        "D.C. Sports Bog",
        "Fantasy Sports",
        "Golf",
        "High School Sports",
        "Olympics",
        "Soccer",
        "Tennis",
        "WNBA",
        "Fancy Stats",
        "Nationals/MLB",
        "Capitals/NHL",
        "AllMetSports",
        "Washington Capitals",
        "D.C. United/Soccer",
        "Wizards/NBA",
        "Redskins/NFL",
        "Colleges",
        "Early Lead",
        "Washington Nationals",
        "Washington Wizards",
        "Soccer Insider",
        "London 2012 Olympics",
        "The Insider",
    ],
    "Arts & Entertainment": [
        "Arts & Entertainment",
        "Arts and Entertainment",
        "Books",
        "Movies",
        "Museums",
        "Music",
        "Pop Culture",
        "Theater & Dance",
        "TV",
        "Comic Riffs",
        "Celebrities",
        "Book Club",
        "Fall TV Preview",
        "Entertainment",
        "Video"
    ],
    "Business": [
        "Business",
        "Economic Policy",
        "Economy",
        "Energy",
        "Health care",
        "Leadership",
        "Markets",
        "Real Estate",
        "Small Business",
        "On Small Business",
        "On Leadership",
        "Where We Live",
        "Capital Business",
        "Fiscal Cliff",
        "Keystone Highway",
        "World Business",
        "Wonkblog",
    ],
    "Personal Finance": [
        "Personal Finance",
        "Get There",
    ],
    "Education": [
        "Education",
        "Higher education",
        "Grade Point",
        "Answer Sheet",
    ],
    "Food": [
        "Food",
        "Voraciously",
    ],
    "Health": [
        "Health",
        "Medical mysteries",
        "Wellness",
        "Health & Science",
        "Health Science",
        "To Your Health",
    ],
    "History": [
        "History",
        "Made by History",
        "Retropolis",
    ],
    "Holiday Guide": [
        "Holiday Gift Guide",
        "Holiday Guide 2012",
    ],
    "Immigration": [
        "Immigration",
    ],
    "Lifestyle": [
        "Lifestyle",
        "Advice",
        "Fashion",
        "Home & Garden",
        "Inspired Life",
        "KidsPost",
        "Parenting",
        "Relationships",
        "Reliable Source",
        "Travel",
        "Solo-ish",
        "Tripping",
        "Weddings",
        "Style",
        "On Parenting",
    ],
    "Magazine": [
        "Magazine",
    ],
    "National Security": [
        "National Security",
        "Foreign Policy",
        "Justice",
        "Military",
        "Josh Rogin",
        "Checkpoint",
    ],
    "Outlook": [
        "Outlook",
        "Book Party",
        "Five Myths",
        "PostEverything",
    ],
    "Science": [
        "Science",
        "Animals",
        "Animalia",
        "Speaking of Science",
    ],
    "Weather": [
        "Weather",
        "Capital Weather Gang",
    ],
    "Photography": [
        "Photography",
        "In Sight",
        "Your Photos",
    ],
    "Puzzles & Games": [
        "Puzzles & Games",
        "Comics",
        "Horoscopes",
    ],
    "Climate & Environment": [
        "Climate & Environment",
        "Energy & Environment",
        "Energy and Environment",
    ],
    "Climate Solutions": [
        "Climate Solutions",
    ],
    "Religion": [
        "Religion",
        "Acts of Faith",
        "On Faith",
    ],
    "National": [
        "National",
        "Post Nation",
        "On Giving",
    ],
    "Obituaries": [
        "Obituaries",
    ],
    "Transportation": [
        "Transportation",
        "Gridlock",
        "Dr. Gridlock",
    ],
    "By The Way": [
        "By The Way",
    ],
    "Carolyn Hax": [
        "Carolyn Hax",
    ],
    "Launcher": [
        "Launcher",
    ],
    "The Lily": [
        "The Lily",
    ],
    "Discussions": [
        "Discussions",
    ],
    "Jobs": [
        "Jobs",
    ],
    "Social Issues": [
        "Social Issues",
    ],
    "She The People": [
        "She The People",
    ],
    "Achenblog": [  # Mix of Science and Politics
        "Achenblog",
    ],
    "ComPost": [  # Journalist's take on news and opinions of the day
        "ComPost",
    ],
    "Express": [  # Was a free daily WP newspaper
        "Express"
    ],
    "El Tiempo Latino": [  # Spanish newspaper, previously owned by WP
        "El Tiempo Latino",
    ],
    "Deportes": [  # ????
        "Deportes",
    ],
    "Ask The Post": [
        "Ask The Post",
    ],
    "Morning Mix": [
        "Morning Mix",
    ],
    "PR": [
        "WashPost PR Blog",
        "PR"
    ],
    "America Answers": [
        "America Answers",
    ],
    "Tablet": [
        "Tablet",  # ???
    ],
    "Test": [
        "Test",
        "Test ",
        "test ",
    ],
    "Storyline": [  # Various categories
        "Storyline",
    ],
    "Rampage": [  # A mixed blog?
        "Rampage",
    ],
    "Events": [
        "Events",
    ],
    "Ads": [
        "Brand Connect",
        "Brand Studio",
    ],
    "Crime": [
        "True Crime",
        "Crime",
    ],
    "Video": [
        "Post Politics Live",
        "Washington Post Live",
        "Post Live",
    ]
}


def get_group(c):
    for k, v in categories.items():
        if c in v:
            return k
    print(f"Category {c} is not mapped. Setting default category instead.")
    return c


def f_print():
    for cat in categories:
        s = ', '.join(categories[cat])
        print(f"{cat}: {s}")
