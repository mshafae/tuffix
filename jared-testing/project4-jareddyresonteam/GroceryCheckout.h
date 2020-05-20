// Written by the one and only Queso Grande (Jared Dyreson)
#ifndef GroceryCheckout_h
#define GroceryCheckout_h

#include <fstream>
#include <map>
#include <vector>

struct GroceryItem{
	GroceryItem(){}
	GroceryItem(const std::string& name, int quantity, float price, bool taxable) : name_(name), quantity_(quantity), price_(price), taxable_(taxable) {}
	std::string	name_;
	int quantity_;
	float	price_;
	bool taxable_;
};

struct ReceiptItem{
	ReceiptItem(){}
	ReceiptItem(const std::string& name, float price) : name_(name), price_(price){}
	ReceiptItem(const GroceryItem& item) : name_(item.name_), price_(item.price_){}
	std::string	name_;
	float	price_;
};

struct Receipt{
	std::vector<ReceiptItem>	item_;
	float total() { return subtotal_ + taxAmount_; }
	float	subtotal_ = 0, taxAmount_ = 0, total_ = (subtotal_+taxAmount_), tr;

};

class GroceryInventory{ // defined in GroceryCheckout.cpp
	public:
		bool AddItem(const std::string& name, int quantity, float price, bool taxable);
		void CreateFromFile(const std::string& fileName);
		Receipt CreateReceipt(const std::string& checkoutFile);
		GroceryItem* FindItem(const std::string& name);
		bool RemoveItem(const std::string& name);
		void SetTaxRate(float taxRate);
		size_t Size();
		void printReciept();

	private:
		std::map<std::string, GroceryItem> mp;
		float tr;
		Receipt r;
};

#endif
