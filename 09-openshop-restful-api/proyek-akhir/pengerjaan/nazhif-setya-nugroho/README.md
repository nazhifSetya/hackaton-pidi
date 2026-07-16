# OpenShop RESTful API

A products CRUD + search REST API built with **Django 4.2 LTS** and **Django REST Framework**, for the Dicoding "OpenShop RESTful API" final submission.

## Requirements

- Python **3.10**
- Pipenv

## Setup & run

```bash
# install dependencies into a Python 3.10 virtualenv
pipenv install

# apply database migrations
pipenv run python manage.py migrate

# run the development server (http://localhost:8000)
pipenv run python manage.py runserver 8000
```

## Endpoints

| Method | URL                  | Description                                  |
| ------ | -------------------- | -------------------------------------------- |
| POST   | `/products`          | Create a product (201)                       |
| GET    | `/products`          | List products (`{ "products": [...] }`)      |
| GET    | `/products?name=`    | Search products by name (case-insensitive)   |
| GET    | `/products?location=`| Search products by location (case-insensitive)|
| GET    | `/products/{id}/`    | Product detail (404 `{"detail":"Not found."}`)|
| PUT    | `/products/{id}/`    | Update a product (200 / 400 / 404)           |
| DELETE | `/products/{id}/`    | Soft delete a product (204)                  |

### Soft delete

`DELETE` marks the product `is_delete = true` instead of removing it. Soft-deleted
products are excluded from list/search but remain accessible via `GET /products/{id}/`
(where `is_delete` will be `true`).

## Testing

Import the Postman collection + environment under
`OpenShopAPITestCollectionAndEnvironment/` (use the **With Soft Delete** variant),
or run them headlessly with newman:

```bash
npx newman run "OpenShopAPITestCollectionAndEnvironment/[743] OpenShop API Test With Soft Delete.postman_collection.json" \
  -e "OpenShopAPITestCollectionAndEnvironment/OpenShop API Test With Soft Delete.postman_environment.json"
```
