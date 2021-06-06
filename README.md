# miro

Create token: https://developers.miro.com/docs/getting-started

Create board:

```
  curl --request POST \
    --url 'https://api.miro.com/v1/boards?fields=foo' \
    --header 'Accept: application/json' \
    --header 'Authorization: Bearer XXX' \
    --header 'Content-Type: application/json' \
    --data '
```

Then run `miro.py` after adding bearer and board ids.
