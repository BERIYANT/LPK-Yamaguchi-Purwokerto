<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Table;

#[Table('finance_categories')]
class FinanceCategory extends LegacyModel
{
    public $timestamps = false;
}
