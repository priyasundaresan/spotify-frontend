import textwrap # Used to abbreviate long song names

# Maps the Spotify API's numerical representation of a musical key to its actual key signature
musical_keys = dict(zip(range(12), ['C', 'C#/D♭', 'D', 'D#/E♭', 'E', 'F', 'F#/G♭', 'G', 'G#/A♭', 'A','A#/B♭', 'B']))

# Draws a horizontal bar graph for a particular audio feature using Google Charts API and Javascript
# X axis is an integer value for a particular audio feature (ex: BPM for tempo, % for danceability); Y axis is each track title
def chart(feature, cache):
    string = [ "function draw_%s() {" % feature.title()]
    if feature == 'key':
        # Adds annotations for the musical key feature to the graph
        string += ["var data = google.visualization.arrayToDataTable([[\'%s\', 'Value', { role: 'annotation' }], %s);" \
                   % (feature.title(), str([[key, cache[key][feature], \
                   musical_keys[cache[key][feature]]] for key in cache if cache[key]])[1:])]
    else:
        string += ["var data = new google.visualization.DataTable();",
                    "data.addColumn('string', \'%s\');" % feature.title(),
                    "data.addColumn('number', 'Value');",
                    "data.addRows(%s);" % str([[key, cache[key][feature]] for key in cache if cache[key]])]
    string += ["var barchart_options = {title: \'%s\'," % feature.upper().replace('_', ' '),
                        "titleTextStyle: {fontSize: 20},\
                        width:550, \
                        height:600, \
                        colors: ['6AE368'], \
                        legend: 'none'};",
                    "var barchart = new google.visualization.BarChart(document.getElementById(\'%s\'));" % feature,
                    "barchart.draw(data, barchart_options);}"]
    return ''.join(string)

# Sets up basic HTML code with a form element to get an artist as input
def setup():
    string = ["<DOCTYPE! html>",
              "<html>",
              "<head>",
              "<meta charset='utf-8'>",
              "<meta name='viewport' content='width=device-width, initial-scale=1, shrink-to-fit=no'>",
              "<meta name='description' content=''>",
              "<meta name='author' content=''>",
              # Uses a bootstrap template
              "<link href='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css' rel='stylesheet'>",
              "<style>",
              "body { padding-top: 54px;}",
              "</style>",
              "<form align='center'><div class='form-group'><fieldset><legend>",
              "<strong><h2>Enter an Artist</h2></strong>",
              "<p>Get a detailed breakdown of the audio features of their top ten hits.</p></legend>",
              "Name:<br><input type='text' name='artist' size='36'><br><br>",
              "<input type='submit' value='Submit'></fieldset></div></form>"]
    return ''.join(string)

def finish_setup():
    return ''.join(["</head>", "</html>"])

# If an artist is not found in the results query, print an error message
def error_msg():
    return "<h2 align='center'>Oops! Didn't find that, please try another artist.</h2>"

# Generates a report about the found artist in tabular format
def report(features, cache, header, image, subheader1, subheader2):
    # Display artist name, genres, and popularity
    string = ["<h1 align='center'>Top Ten Hits Analytics: <strong>%s</strong></h1><br>" % header]
    if image:
        string += ["<p style='text-align:center;'><img src=\'%s\'></p>" % image]
    string += ["<h3 align='center'><strong>genres:</strong> %s</h3>" % subheader1,
              "<h3 align='center'><strong>popularity rating:</strong> %s/100</h3>" % subheader2]
    previews = [[key, cache[key]['preview']] for key in cache if cache[key] and 'preview' in cache[key]]
    # Input 30-second audio samples into a 5 x 2 table
    if previews:
        previewTableOffset = 0
        string += ["<br><br><table align='center'>"]
        for [track, preview] in previews:
            if previewTableOffset % 5 == 0:
                string += ["<tr>"]
            string += ["<td><video width='300' height='60' controls='' name='media'> \
                       <source src=\'%s\' type='audio/mpeg'></video>" % preview,
                       "<h4 align='center'>%s</h4></td>" % textwrap.shorten(track, width=33, placeholder="...")]
            if previewTableOffset % 5 == 4:
                string += ["</tr>"]
            previewTableOffset += 1
    # Load bar graphs corresponding to each audio feature
    string += ["</table><script type='text/javascript' src='https://www.gstatic.com/charts/loader.js'></script>",
              "<script type='text/javascript'>",
              "google.charts.load('current', {'packages':['corechart']});"]
    for feature in features:
        string.append("google.charts.setOnLoadCallback(draw_%s);" % feature.title())
    for feature in features:
        string.append(chart(feature, cache))
    # Add closing tags to the previews section and begin charts section
    string += ["</script>",
               "</head>",
               "<body>",
               "<br><br>",
               "<table align='center'>"]
    # Input charts into a 3 x 3 table
    graphTableOffset = 0
    for feature in features:
        if graphTableOffset % 3 == 0:
            string += ["<tr>"]
        string += ["<td><div id=\'%s\'></div></td>" % feature]
        if graphTableOffset % 3 == 2:
            string += ["</tr>"]
        graphTableOffset += 1
    # Create a legend for all of the charts shown
    string += ["</table>",
               "<ul style='text-align:center; list-style-type: none;'>",
               "<li><strong>acoustic</strong> – how nonelectric it sounds</li>",
               "<li><strong>danceability</strong> – how easy it is to dance along </li>",
               "<li><strong>energy</strong> – how intense it sounds</li>",
               "<li><strong>liveness</strong> – how live it sounds (vs. recorded)</li>",
               "<li><strong>key</strong> – the key the song is in (C = 0, C#/D♭ = 1, D = 2, ...)</li>",
               "<li><strong>valence</strong> – how positive/happy it sounds (positive = 1, negative = 0 )</li>",
               "<li><strong>tempo</strong> – how upbeat it is (BPM)</li>",
               "<li><strong>mode</strong> – how major/minor it sounds (major = 1, minor = 0)</li>",
               "<li><strong>time signature</strong> – how many beats per measure (4 = 4/4 (common time), 3 = 3/4, ...)</li>",
               "</ul>",
               "</body>", "</html>"]
    return ''.join(string)
