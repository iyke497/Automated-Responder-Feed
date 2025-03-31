# Pull FMOH Financial Allocation Responses
curl -X GET "https://api.eyemark.ng/api/surveys/f0a3d43b-f7ee-4417-a338-7ba33ab9da14/responses/?limit=25" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUwODU1NTc0LCJpYXQiOjE3NDMwNzk1NzQsImp0aSI6IjBhNDg3ZWI5YmVlZjQwYTBiMjIyMmQ1Yjc1ZGQ0MDZiIiwidXNlcl9pZCI6NjI4fQ.Lsxg__plY4Z7GHN1uJ9X5yNCSW3VJnGI75I57WjwyRk"


# Pull FMOH organizations
curl -X GET "https://api.eyemark.ng/api/users/visitor-organizations/?limit=10&offset=0" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUwODU1NTc0LCJpYXQiOjE3NDMwNzk1NzQsImp0aSI6IjBhNDg3ZWI5YmVlZjQwYTBiMjIyMmQ1Yjc1ZGQ0MDZiIiwidXNlcl9pZCI6NjI4fQ.Lsxg__plY4Z7GHN1uJ9X5yNCSW3VJnGI75I57WjwyRk"

curl -X GET "https://api.eyemark.ng/api/users/visitor-organizations/" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUwODU1NTc0LCJpYXQiOjE3NDMwNzk1NzQsImp0aSI6IjBhNDg3ZWI5YmVlZjQwYTBiMjIyMmQ1Yjc1ZGQ0MDZiIiwidXNlcl9pZCI6NjI4fQ.Lsxg__plY4Z7GHN1uJ9X5yNCSW3VJnGI75I57WjwyRk" -H "Organization_id: ac027fd7-96b5-4b0b-bcfc-a1d07ac0d33f"