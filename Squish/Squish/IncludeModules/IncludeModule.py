import sys 
# Include folder with "mymodule.py" in Python's search path:
sys.path.append("D:\Work\Git\Squish\Squish\IncludeModules\MyModule.py")
import MyModule
'''
sys.path.append( ".\root" )
from .root import MyModule3
sys.path.append( ".\root\test" )
from .test import MyModule2
'''
'''
import root.test.MyModule2
import root.MyModule3
'''
import imp
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))

def main():
        #startApplication("my_aut")
        #mymodule.click_button(":object_name")
        print ("In the Main")
        MyModule.Module_click_button(":Test")        
        '''
        MyModule3.Module_TestModule3(":Test")
        MyModule2.Module_TestModule(":Test")
        '''
        foo3= imp.load_source('MyModule3.py', 'D:/Work/Git/Squish/Squish/IncludeModules/root')
        foo3.Module_TestModule3(":Test")
 
        foo2= imp.load_source('MyModule2.py', 'D:/Work/Git/Squish/Squish/IncludeModules/root/test')
        foo2.Module_TestModule2(":Test")
        

if __name__ == "__main__":
        main()
