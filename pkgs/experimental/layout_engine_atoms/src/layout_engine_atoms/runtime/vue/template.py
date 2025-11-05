from __future__ import annotations

_HTML_TEMPLATE = """<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>{title}</title>
    <link rel=\"stylesheet\" href=\"./static/swarma-vue/style.css\" />
    <style>
      :root {{
        color-scheme: dark;
      }}
      body {{
        margin: 0;
        font-family: \"Inter\", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
        background: radial-gradient(circle at top, #0f172a, #020617 55%);
        color: #f8fafc;
        min-height: 100vh;
      }}
      main {{
        max-width: 1328px;
        margin: 0 auto;
        padding: 2rem 1.5rem 4rem;
      }}
      .shell-card {{
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(148, 163, 184, 0.15);
        backdrop-filter: blur(40px);
        border-radius: 24px;
        padding: 1.5rem;
        box-shadow: 0 24px 80px rgba(15, 23, 42, 0.45);
        overflow: auto;
      }}
      #app {{
        min-height: 100vh;
      }}
    </style>
    <script type=\"importmap\">
      {{
        \"imports\": {{
          \"vue\": \"https://cdn.jsdelivr.net/npm/vue@3/dist/vue.esm-browser.js\",
          \"eventemitter3\": \"https://cdn.jsdelivr.net/npm/eventemitter3@5/dist/eventemitter3.esm.js\",
          \"@swarmakit/vue\": \"./static/swarma-vue/vue.js\"
        }}
      }}
    </script>
  </head>
  <body>
    <main>
      <section class=\"shell-card\">
        <div id=\"app\"></div>
      </section>
    </main>
    <script type=\"module\">
      const manifestUrl = './manifest.json';
      const muxUrl = undefined;

      async function bootstrap() {{
        const [{{ createApp }}, engineModule] = await Promise.all([
          import('vue'),
          import('./static/layout-engine-vue/index.js'),
        ]);

        const engine = await engineModule.createLayoutEngineApp({{
          manifestUrl,
          muxUrl,
        }});

        const App = {{
          components: {{
            LayoutEngineShell: engineModule.LayoutEngineShell,
            LayoutEngineNavLink: engineModule.LayoutEngineNavLink,
          }},
          template: `
            <LayoutEngineShell>
              <template #default=\"{{ site }}\">
                <nav v-if=\"site.pages.value.length\">
                  <LayoutEngineNavLink
                    v-for=\"page in site.pages.value\"
                    :key=\"page.id\"
                    :page-id=\"page.id\"
                  >
                    {{{{ page.title ?? page.id }}}}
                  </LayoutEngineNavLink>
                </nav>
              </template>
            </LayoutEngineShell>
          `,
        }};

        const app = createApp(App);
        app.use(engine.plugin);
        app.mount('#app');
      }}

      bootstrap().catch((error) => {{
        console.error('Failed to bootstrap layout app', error);
        const el = document.getElementById('app');
        if (el) {{
          el.innerHTML = '<p style=\"padding:1.5rem;text-align:center;\">Failed to load dashboard. Check server logs.</p>';
        }}
      }});
    </script>
  </body>
</html>
"""


def render_shell(*, title: str) -> str:
    return _HTML_TEMPLATE.format(title=title)
