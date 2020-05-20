// Written by the one and only Queso Grande (Jared Dyreson)
#include	<iostream>
#include	"GroceryCheckout.h"

bool GroceryInventory::AddItem(const std::string& name, int quantity, float price, bool taxable) {
	for(auto element : mp){
		if(element.first == name){ return false; }
	}
	mp.emplace(std::make_pair(name, GroceryItem(name, quantity, price, taxable)));
	return true;
}

void GroceryInventory::CreateFromFile(const std::string& fileName){
  std::ifstream	file(fileName);
	std::string	name_;
	float price_;
	int quantity_;
	bool taxable_;
	if(!file.is_open()){
		std::cerr << "cannot open file, cowardly refusing" << std::endl;
		exit(1);
	}
	while(!file.eof()){
		file >> name_ >> quantity_ >> price_ >> taxable_;
		AddItem(name_, quantity_, price_, taxable_);
	}
}

Receipt GroceryInventory::CreateReceipt(const std::string& fileName){
	std::fstream file(fileName);
	std::string line_;
	r.tr = tr;
 	while(std::getline(file, line_)){
		if(line_.empty()) { continue; }
		auto grocery = FindItem(line_);
		grocery->quantity_--;
		r.subtotal_+=grocery->price_;
		if(grocery->taxable_){ r.taxAmount_+=(grocery->price_ * (r.tr)); }
		r.item_.emplace_back(ReceiptItem(*grocery));
	}
	r.total_ = (r.taxAmount_ + r.subtotal_);
	return r;
}

GroceryItem*	GroceryInventory::FindItem(const std::string& name) {
	for(auto element : mp){
		if(element.first == name){ return &(mp.at(name)); }
	}
	return nullptr;
}

bool GroceryInventory::RemoveItem(const std::string& name){
	if(mp.find(name) != mp.end()) { mp.erase(name); return true; }
	return false;
}

void GroceryInventory::SetTaxRate(float taxRate_){
	if(taxRate_ > 1) { taxRate_*=.01; } // if the tax rate is given as a percentage out of 100, convert it to proper notation
	tr = taxRate_;
}

size_t GroceryInventory::Size(){ return mp.size(); }
