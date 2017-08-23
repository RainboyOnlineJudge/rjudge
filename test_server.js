var app = require('express')()
var bodyParser = require('body-parser');

app.use(bodyParser.json());

app.get('/', function (req, res) {
  res.send('Hello World!');
});

app.post('/data', function (req, res) {
  console.log(req.body)
  res.json(req.body)
});

var server = app.listen(3000, function () {
  var host = server.address().address;
  var port = server.address().port;

  console.log('Example app listening at http://%s:%s', host, port);
});
