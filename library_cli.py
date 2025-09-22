# library_cli.py
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def add_member(name, email):
    resp = sb.table("members").insert({"name": name, "email": email}).execute()
    return resp.data

def add_book(title, author, category, stock):
    resp = sb.table("books").insert({"title": title, "author": author, "category": category, "stock": stock}).execute()
    return resp.data

def list_books():
    resp = sb.table("books").select("*").order("title", desc=False).execute()
    return resp.data

def search_books(query):
    # simple ILIKE search on title/author/category
    q = f"%{query}%"
    resp = sb.table("books").select("*").or_(
        f"title.ilike.{q},author.ilike.{q},category.ilike.{q}"
    ).execute()
    return resp.data

def show_member(member_id):
    resp = sb.table("members").select(", borrow_records()").eq("member_id", member_id).execute()
    return resp.data

def update_book_stock(book_id, new_stock):
    resp = sb.table("books").update({"stock": new_stock}).eq("book_id", book_id).execute()
    return resp.data

def update_member_email(member_id, new_email):
    resp = sb.table("members").update({"email": new_email}).eq("member_id", member_id).execute()
    return resp.data

def delete_member(member_id):
    # Only allow delete if member has no outstanding borrows
    outstanding = sb.table("borrow_records").select("*").eq("member_id", member_id).is_("return_date", None).execute()
    if outstanding.data and len(outstanding.data) > 0:
        raise Exception("Cannot delete member: outstanding borrowed books exist.")
    resp = sb.table("members").delete().eq("member_id", member_id).execute()
    return resp.data

def delete_book(book_id):
    outstanding = sb.table("borrow_records").select("*").eq("book_id", book_id).is_("return_date", None).execute()
    if outstanding.data and len(outstanding.data) > 0:
        raise Exception("Cannot delete book: currently borrowed.")
    resp = sb.table("books").delete().eq("book_id", book_id).execute()
    return resp.data

def borrow_book_rpc(member_id, book_id):
    try:
        resp = sb.rpc("borrow_book", {"p_member_id": member_id, "p_book_id": book_id}).execute()
        if not resp.data:
            print("Borrow failed (maybe no stock or invalid input).")
        else:
            print("Borrowed successfully:", resp.data)
    except Exception as e:
        print("Borrow error:", e)


def return_book_rpc(member_id, book_id):
    try:
        resp = sb.rpc("return_book", {"p_member_id": member_id, "p_book_id": book_id}).execute()
        if not resp.data:
            print("Return failed (maybe invalid record).")
        else:
            print("Returned successfully:", resp.data)
    except Exception as e:
        print("Return error:", e)


# ===== Reports =====
def top_most_borrowed(limit=5):
    resp = sb.table("most_borrowed_books").select("*").limit(limit).execute()
    return resp.data

def list_overdue_members():
    resp = sb.table("overdue_members").select("*").execute()
    return resp.data

def count_borrowed_per_member():
    resp = sb.table("borrowed_count_per_member").select("*").execute()
    return resp.data

# ===== Simple CLI =====
def main_menu():
    MENU = """
1) Register member
2) Add book
3) List all books
4) Search books
5) Show member and borrowed books
6) Update book stock
7) Update member email
8) Delete member
9) Delete book
10) Borrow book
11) Return book
12) Reports
0) Exit
Choose: """
    while True:
        try:
            choice = input(MENU).strip()
            if choice == "1":
                name = input("Name: ").strip()
                email = input("Email: ").strip()
                print(add_member(name, email))
            elif choice == "2":
                title = input("Title: ").strip()
                author = input("Author: ").strip()
                category = input("Category: ").strip()
                stock = int(input("Stock: ").strip())
                print(add_book(title, author, category, stock))
            elif choice == "3":
                for b in list_books():
                    print(b)
            elif choice == "4":
                q = input("Query (title/author/category): ").strip()
                for b in search_books(q):
                    print(b)
            elif choice == "5":
                mid = int(input("Member ID: ").strip())
                print(show_member(mid))
            elif choice == "6":
                bid = int(input("Book ID: ").strip())
                ns = int(input("New stock: ").strip())
                print(update_book_stock(bid, ns))
            elif choice == "7":
                mid = int(input("Member ID: ").strip())
                new_email = input("New email: ").strip()
                print(update_member_email(mid, new_email))
            elif choice == "8":
                mid = int(input("Member ID to delete: ").strip())
                print(delete_member(mid))
            elif choice == "9":
                bid = int(input("Book ID to delete: ").strip())
                print(delete_book(bid))
            elif choice == "10":
                mid = int(input("Member ID: ").strip())
                bid = int(input("Book ID: ").strip())
                borrow_book_rpc(mid, bid)

            elif choice == "11":
                mid = int(input("Member ID: ").strip())
                bid = int(input("Book ID: ").strip())
                return_book_rpc(mid, bid)

            elif choice == "12":
                print("\nTop borrowed:")
                for row in top_most_borrowed():
                    print(row)
                print("\nOverdue members:")
                for row in list_overdue_members():
                    print(row)
                print("\nBorrow count per member:")
                for row in count_borrowed_per_member():
                    print(row)
            elif choice == "0":
                break
            else:
                print("Invalid choice")
        except Exception as e:
            print("ERROR:", e)

if __name__ == "__main__":
    main_menu()