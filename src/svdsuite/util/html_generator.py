import itertools
import gzip
import base64
import lxml.etree


class HTMLGenerator:
    html_packer_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>Reslover Log</title>
          <script src="https://cdn.jsdelivr.net/npm/fflate"></script>
        </head>
        <body>
        <script>
            // The Gzip-compressed string (Base64 encoded)
            const compressedDataBase64 = "COMPRESSED_DATA";

            // Decode Base64 and decompress using fflate
            const compressedData = Uint8Array.from(atob(compressedDataBase64), c => c.charCodeAt(0));
            const decompressed = fflate.gunzipSync(compressedData);

            // Decode the decompressed content into a string
            const htmlContent = new TextDecoder().decode(decompressed);

            // Replace the current document with the decompressed content
            const parser = new DOMParser();
            const doc = parser.parseFromString(htmlContent, "text/html");

            // Replace the current document's body and head
            document.documentElement.innerHTML = doc.documentElement.innerHTML;

            // Manually execute all scripts in the new document
            document.querySelectorAll("script").forEach(oldScript => {{
                const newScript = document.createElement("script");
                if (oldScript.src) {{
                    // Re-attach external scripts
                    newScript.src = oldScript.src;
                }} else {{
                    // Re-execute inline scripts
                    newScript.textContent = oldScript.textContent;
                }}
                document.body.appendChild(newScript);
            }});
        </script>
        </body>
        </html>
    """

    html_content_template = """
        <!DOCTYPE html>
        <html>
          <head>
            <script src="http://code.jquery.com/jquery-1.11.1.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/svg-pan-zoom@3.5.0/dist/svg-pan-zoom.min.js"></script>

            <meta name="viewport" content="user-scalable=no, width=device-width, initial-scale=1, maximum-scale=1">
            <style>
              html, body {
                width: auto;
                height: 100%;
                margin: 10px;
              }

              .ctrl-overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.0); /* Semi-transparent black */
                color: red;
                display: flex;
                font-size: 1.2em;
                padding: 10px;
                z-index: 10;
                pointer-events: none; /* Allow clicks to pass through the overlay */
                visibility: hidden; /* Initially hidden */
              }

              .svg-container {
                position: relative; /* Ensure proper positioning for the overlay */
              }

              .scrollable-div {
                overflow-x: auto;
                overflow-y: auto;
                max-height: 200px;
                white-space: nowrap;
                padding: 15px;
                background-color: #ddd;
                margin-bottom: 20px;
                border: 1px solid black;
            }
            </style>
          </head>
          <body>
            BODY_CONTENT

            <script>
              window.onload = function () {
                var panZoomInstances = [];

                function createPanZoomWithOverlay(container, svgSelector) {
                  // Get the SVG element inside the container
                  const svgElement = container.querySelector(svgSelector);

                  // Create an overlay specific to this container
                  const overlay = document.createElement('div');
                  overlay.className = 'ctrl-overlay';
                  overlay.textContent = 'Hold "Ctrl" to Zoom and Pan';
                  container.appendChild(overlay);

                  // Initialize svgPanZoom with custom behavior
                  const panZoomInstance = svgPanZoom(svgElement, {
                    zoomEnabled: true,
                    controlIconsEnabled: true,
                    fit: 0,
                    center: 1,
                    maxZoom: 100,
                    minZoom: 0.01,
                    zoomScaleSensitivity: 0.5,
                    customEventsHandler: {
                      init: function (options) {
                        options.instance.disableZoom();
                        options.instance.disablePan();

                        document.body.addEventListener("keydown", function (e) {
                          if (e.key === "Control") {
                            options.instance.enableZoom();
                            options.instance.enablePan();
                            overlay.style.visibility = 'hidden'; // Hide overlay
                          }
                        });

                        document.body.addEventListener("keyup", function (e) {
                          if (e.key === "Control") {
                            options.instance.disableZoom();
                            options.instance.disablePan();
                            overlay.style.visibility = 'visible'; // Show overlay
                          }
                        });
                      },
                      destroy: function (options) {}
                    }
                  });

                  // Show the overlay initially
                  overlay.style.visibility = 'visible';

                  return panZoomInstance;
                }

                // Dynamically find all svg-container divs and create panZoom instances
                const svgContainers = document.querySelectorAll('div.svg-container');
                svgContainers.forEach((container, index) => {
                  const svgId = `#svg${index + 1}`;
                  panZoomInstances.push(createPanZoomWithOverlay(container, svgId));
                });

                // Resize function to apply changes to all panZoom instances
                function resizeAllPanZoom() {
                  panZoomInstances.forEach(function (panZoomInstance) {
                    panZoomInstance.resize();
                    panZoomInstance.fit();
                    panZoomInstance.center();
                  });
                }

                $(window).resize(resizeAllPanZoom);
              };
            </script>
          </body>
        </html>
    """

    svg_container_template = (
        '<div class="svg-container" style="width: 100%; height: 60%; border:1px solid black;">SVG_CONTENT</div>\n'
    )

    def __init__(self, output_file: str):
        self._output_file = output_file
        self._svd_counter = itertools.count(1)
        self._html_file_generated = False
        self._body_content = ""
        self._svg_pan_zoom_instances = ""

    def __del__(self):
        self.generate_html_file()

    def add_svg(self, svg_content: str):
        svg_count = next(self._svd_counter)
        self._body_content += self.svg_container_template.replace(
            "SVG_CONTENT", self._modify_svg(svg_content, svg_count)
        )

    def add_h1(self, text: str):
        self._body_content += f"<h1>{text}</h1>\n"

    def add_h2(self, text: str):
        self._body_content += f"<h2>{text}</h2>\n"

    def add_h3(self, text: str):
        self._body_content += f"<h3>{text}</h3>\n"

    def add_h4(self, text: str):
        self._body_content += f"<h4>{text}</h4>\n"

    def add_h5(self, text: str):
        self._body_content += f"<h5>{text}</h5>\n"

    def add_h6(self, text: str):
        self._body_content += f"<h6>{text}</h6>\n"

    def add_scrollable_div_with_description(self, description: str, content: str):
        self._body_content += f'{description}: <div class="scrollable-div">{content}</div>\n'

    def add_paragraph(self, text: str):
        self._body_content += f"<p>{text}</p>\n"

    def generate_html_file(self):
        if self._html_file_generated:
            return
        self._html_file_generated = True

        compressed_data = self._compress_with_gzip()

        with open(self._output_file, "w", encoding="utf-8") as file:
            file.write(self.html_packer_template.replace("COMPRESSED_DATA", compressed_data))

    def _modify_svg(self, svg_content: str, svg_count: int) -> str:
        # Parse the XML content into an lxml tree
        parser = lxml.etree.XMLParser(remove_comments=True)
        tree = lxml.etree.fromstring(svg_content.encode("utf-8"), parser=parser)

        # Modify the <svg> element attributes
        tree.attrib.clear()  # Clear all existing attributes
        tree.attrib.update(
            {
                "id": f"svg{svg_count}",
                "xmlns": "http://www.w3.org/2000/svg",
                "style": "display: inline; width: 100%; height: 100%;",
                "version": "1.1",
            }
        )

        # Serialize the modified tree back to a string
        return lxml.etree.tostring(tree, pretty_print=True, encoding="unicode")

    def _compress_with_gzip(self) -> str:
        html_content = self.html_content_template.replace("BODY_CONTENT", self._body_content)
        html_content = html_content.replace("SVG_PAN_ZOOM_INSTANCES", self._svg_pan_zoom_instances)

        # Compress the HTML content using gzip
        compressed_data = gzip.compress(html_content.encode("utf-8"))
        # Base64 encode the compressed data for embedding in HTML
        return base64.b64encode(compressed_data).decode("utf-8")
