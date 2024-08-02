
def genrate_html(data):
  html = '''
  <style>
      table {
          width: 100%;
          border-collapse: collapse;
          margin: auto;
          font-size: 18px;
          text-align: left;
      }
      th, td {
          padding: 12px;
          border: 1px solid #ddd;
      }
      th {
          background-color: #f2f2f2;
      }
      tr:nth-child(even) {
          background-color: #f9f9f9;
      }
      tr:hover {
          background-color: #f1f1f1;
      }
      .nested-table {
          width: 100%;
          margin: 10px 0;
      }
  </style>
  <table>
  '''
  for key, value in data.items():
      if isinstance(value, dict):
          html += f'<tr><th colspan="2">{key}</th></tr>'
          for sub_key, sub_value in value.items():
              html += f'<tr><td>{sub_key}</td><td>{sub_value}</td></tr>'
      elif isinstance(value, list):
          html += f'<tr><th colspan="2">{key}</th></tr>'
          for item in value:
              if isinstance(item, dict):
                  html += '<tr><td colspan="2"><table class="nested-table">'
                  for sub_key, sub_value in item.items():
                      if isinstance(sub_value, list):
                          html += f'<tr><td>{sub_key}</td><td>{"<br>".join(sub_value)}</td></tr>'
                      else:
                          html += f'<tr><td>{sub_key}</td><td>{sub_value}</td></tr>'
                  html += '</table></td></tr>'
              else:
                  html += f'<tr><td colspan="2">{item}</td></tr>'
      else:
          html += f'<tr><td>{key}</td><td>{value}</td></tr>'
  html += '</table>'
  return html
