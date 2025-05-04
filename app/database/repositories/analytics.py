# // 1.  Overview API
# //     * Provides data for the main dashboard overview.
# router.get('/overview', async (req, res) => {
#     try {
#         // a.  Total Number of Sales (Including All Chemists) - Chart 1
#         const allSales = await Order.countDocuments();

#         // b.  Total Number of Sales Per Chemist - Chart 2
#         const salesPerChemist = await Order.aggregate([
#             {
#                 $group: {
#                     _id: '$chemist_id',
#                     totalSales: { $sum: 1 }
#                 }
#             },
#             {
#                 $lookup: {  // Join to get chemist name
#                     from: 'chemists',
#                     localField: '_id',
#                     foreignField: 'user_id',
#                     as: 'chemist'
#                 }
#             },
#             {
#                 $unwind: '$chemist'
#             },
#             {
#                 $project: {
#                     _id: 0,
#                     chemist_id: '$_id',
#                     chemist_name: '$chemist.name',
#                     totalSales: 1
#                 }
#             },
#             {
#                 $sort: { totalSales: -1 } // Sort by sales, descending
#             }
#         ]);

#         res.json({
#             success: true,
#             data: {
#                 allSales,
#                 salesPerChemist
#             }
#         });
#     } catch (error) {
#         console.error(error);
#         res.status(500).json({ success: false, message: 'Internal server error' });
#     }
# });

# // 2.  Pharmacy Management API
# //     * Provides data for managing chemists.
# router.get('/pharmacy-management/chemists', async (req, res) => {
#     try {
#         const chemists = await Chemist.find({}, {
#             _id: 1,
#             user_id: 1,
#             'name.first_name': 1,
#             'name.last_name': 1,
#             store_name: 1,
#             'address.city': 1,
#             'address.state': 1,
#             dl_number: 1
#         }); // Fetch only required fields

#         res.json({ success: true, data: chemists });
#     } catch (error) {
#         console.error(error);
#         res.status(500).json({ success: false, message: 'Internal server error' });
#     }
# });

# //   * Get a single chemist details
# router.get('/pharmacy-management/chemists/:chemistId', async (req, res) => {
#     try {
#         const chemistId = req.params.chemistId;
#         const chemist = await Chemist.findOne({ user_id: chemistId }, {
#             _id: 1,
#             user_id: 1,
#             name: 1,
#             store_name: 1,
#             address: 1,
#             phone_number: 1,
#             dl_number: 1,
#             created_at: 1,
#             updated_at: 1
#         });

#         if (!chemist) {
#             return res.status(404).json({ success: false, message: 'Chemist not found' });
#         }

#         res.json({ success: true, data: chemist });
#     } catch (error) {
#         console.error(error);
#         res.status(500).json({ success: false, message: 'Internal server error' });
#     }
# });



# // 3.  Report and Analysis API
# //     * Provides data for detailed sales reports and analysis.
# router.get('/report-and-analysis/sales', async (req, res) => {
#     try {
#         const { startDate, endDate } = req.query;
#         const start = new Date(startDate);
#         const end = new Date(endDate);

#         // 1. Find the top 5 chemists by total sales
#         const top5Chemists = await Order.aggregate([
#             {
#                 $match: {
#                     order_date: { $gte: start, $lte: end }
#                 }
#             },
#             {
#                 $group: {
#                     _id: '$chemist_id',
#                     totalSales: { $sum: '$total_amount' }
#                 }
#             },
#             {
#                 $sort: { totalSales: -1 }
#             },
#             {
#                 $limit: 5
#             }
#         ]);

#         // 2. Extract the chemist IDs of the top 5
#         const top5ChemistIds = top5Chemists.map(chemist => chemist._id);

#         // 3. Get sales data for the top 5 chemists
#         const salesData = await Order.aggregate([
#             {
#                 $match: {
#                     order_date: { $gte: start, $lte: end },
#                     chemist_id: { $in: top5ChemistIds }  // Filter by top 5 chemist IDs
#                 }
#             },
#             {
#                 $lookup: {  // Join with SaleDetails to get item details
#                     from: 'saledetails',
#                     localField: '_id',
#                     foreignField: 'sale_id',
#                     as: 'items'
#                 }
#             },
#             {
#                 $unwind: '$items'
#             },
#             {
#                 $lookup: {  // Join with Products to get product names
#                     from: 'products',
#                     localField: 'items.product_id',
#                     foreignField: '_id',
#                     as: 'product'
#                 }
#             },
#             {
#                 $unwind: '$product'
#             },
#             {
#                 $group: {
#                     _id: {
#                         order_id: '$_id',
#                         order_date: '$order_date',
#                         chemist_id: '$chemist_id',
#                         product_id: '$items.product_id',
#                         product_name: '$product.product_name', // Get product name
#                         unit_price: '$items.unit_price',
#                         quantity: '$items.quantity'
#                     },
#                     total_order_amount: { $first: '$total_amount' }

#                 }
#             },
#             {
#                 $project: { // Shape the output
#                     _id: 0,
#                     order_id: '$_id.order_id',
#                     order_date: '$_id.order_date',
#                     chemist_id: '$_id.chemist_id',
#                     product_id: '$_id.product_id',
#                     product_name: '$_id.product_name', // Include product name
#                     unit_price: '$_id.unit_price',
#                     quantity: '$_id.quantity',
#                     item_amount: { $multiply: ['$_id.unit_price', '$_id.quantity'] },
#                     total_order_amount: 1
#                 }
#             },
#             {
#                 $sort: { order_date: 1 }
#             }
#         ]);

#         res.json({ success: true, data: salesData });
#     } catch (error) {
#         console.error(error);
#         res.status(500).json({ success: false, message: 'Internal server error' });
#     }
#     });

# module.exports = router;
