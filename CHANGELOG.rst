Changelog
---------

 2011-08-25: v1.1.0
  * Modified OAuthAdapter to raise an APIException when any API errors occur.
  * Added get_activity() method to return subscriber analytics activity.
  * Modified create() method to return the instance of the newly created Resource instead of true.
  * Fixed bugs in find and findSubscribers methods when no matches are found.
